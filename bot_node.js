const puppeteer = require('puppeteer-core');
const fs = require('fs');
const csv = require('csv-parser');

async function runBot() {
    console.log("🤖 Lendo CSV...");
    const posts = [];
    await new Promise((resolve) => {
        fs.createReadStream('cronograma_comunidade.csv')
            .pipe(csv())
            .on('data', (data) => posts.push(data))
            .on('end', () => resolve());
    });

    console.log("🚀 Conectando ao Chrome na porta 9222...");
    const browser = await puppeteer.connect({
        browserURL: 'http://127.0.0.1:9222',
        defaultViewport: null
    });

    try {
        let page = await browser.newPage();

        console.log("🌍 Navegando para o YouTube Studio...");
        await page.goto("https://studio.youtube.com/", { waitUntil: 'domcontentloaded', timeout: 60000 });

        console.log("🌍 Clicando no botão Criar do cabeçalho...");
        await page.waitForSelector('.ytcpAppHeaderCreateIcon', { timeout: 30000 });
        await page.click('.ytcpAppHeaderCreateIcon');
        await new Promise(r => setTimeout(r, 2000));
        
        // Find the "Create post" button inside the menu and click it
        const createPostBtn = await page.$$("::-p-xpath(//tp-yt-paper-item[contains(., 'Create post') or contains(., 'Criar postagem')])");
        if (createPostBtn.length > 0) {
            await createPostBtn[0].click();
        } else {
            console.error("❌ Não achou o botão Criar Postagem no menu!");
            return;
        }
        
        console.log("➡️ Aguardando a nova aba abrir...");
        await new Promise(r => setTimeout(r, 5000));
        
        let allPages = await browser.pages();
        let postPage = allPages.find(p => p.url().includes('/posts') || p.url().includes('/community'));
        
        if (!postPage) {
            console.error("❌ Aba de postagem não foi aberta!");
            return;
        }
        
        console.log(`✅ Encontrou a aba de postagem: ${postPage.url()}`);
        await postPage.bringToFront();
        
        // Substitui a 'page' antiga pela nova aba
        page = postPage;

        for (let i = 0; i < posts.length; i++) {
            const p = posts[i];
            const isFirstDay = i < 2;

            console.log(`⏳ Post ${i+1}/${posts.length}...`);

            // Tenta clicar no placeholder primeiro para ativar a caixa
            const placeholder = await page.$('#commentbox-placeholder');
            if (placeholder) {
                try {
                    await placeholder.click();
                    await new Promise(r => setTimeout(r, 1000));
                } catch (e) {}
            }

            // Agora a caixa deve estar visível e clicável
            await page.click('div#contenteditable-root');
            await new Promise(r => setTimeout(r, 500));
            
            // Limpa e digita
            await page.evaluate(() => { document.querySelector('div#contenteditable-root').innerText = ''; });
            
            // Type the text line by line
            const lines = p.texto.split('\n');
            for (let j = 0; j < lines.length; j++) {
                await page.keyboard.type(lines[j], { delay: 5 });
                if (j < lines.length - 1) {
                    await page.keyboard.down('Shift');
                    await page.keyboard.press('Enter');
                    await page.keyboard.up('Shift');
                }
            }
            await new Promise(r => setTimeout(r, 1000));

            // dispatch input event
            await page.evaluate(() => {
                const b = document.querySelectorAll('div#contenteditable-root')[0];
                if (b) b.dispatchEvent(new InputEvent('input', {bubbles:true}));
            });
            await new Promise(r => setTimeout(r, 2000));

            if (isFirstDay) {
                console.log("🚀 Publicando agora...");
                const postBtn = await page.$('ytd-button-renderer#submit-button button');
                if (postBtn) await postBtn.click();
                await new Promise(r => setTimeout(r, 5000));
            } else {
                console.log(`⏰ Agendando para ${p.data} ${p.hora}...`);
                const schedBtn = await page.$('ytd-button-renderer#schedule-button button');
                if (schedBtn) await schedBtn.click();
                await new Promise(r => setTimeout(r, 2000));

                const datePicker = await page.$('ytcp-text-dropdown-trigger#datepicker-trigger');
                if (datePicker) await datePicker.click();
                await new Promise(r => setTimeout(r, 1000));
                
                await page.keyboard.down('Control');
                await page.keyboard.press('a');
                await page.keyboard.up('Control');
                await page.keyboard.type(p.data);
                await page.keyboard.press('Enter');
                await new Promise(r => setTimeout(r, 1000));

                const timePicker = await page.$('ytcp-text-dropdown-trigger#time-of-day-trigger');
                if (timePicker) await timePicker.click();
                await new Promise(r => setTimeout(r, 1000));

                await page.keyboard.down('Control');
                await page.keyboard.press('a');
                await page.keyboard.up('Control');
                await page.keyboard.type(p.hora);
                await page.keyboard.press('Enter');
                await new Promise(r => setTimeout(r, 1000));

                const modalBtn = await page.$('ytcp-button#submit-button button');
                if (modalBtn) await modalBtn.click();
                await new Promise(r => setTimeout(r, 5000));
            }

            console.log(`✅ Post ${i+1} concluído!`);
            await page.reload({ waitUntil: 'networkidle2' });
            await new Promise(r => setTimeout(r, 5000));
        }

        console.log("🎉 FINALIZADO!");

    } catch (e) {
        console.error("❌ Erro:", e);
    } finally {
        await browser.disconnect();
    }
}

runBot();
