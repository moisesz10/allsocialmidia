const fs = require('fs');
const puppeteer = require('puppeteer-core');
const { parse } = require('csv-parse/sync');

// Utilitário para pausar a execução
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function runInstagramBot() {
    console.log("Iniciando Bot do Instagram (Meta Business Suite)...");

    // Lendo o CSV
    const csvData = fs.readFileSync('cronograma_instagram.csv', 'utf8');
    const records = parse(csvData, {
        columns: true,
        skip_empty_lines: true
    });

    console.log(`Foram encontrados ${records.length} posts para agendar.`);

    const browser = await puppeteer.connect({
        browserURL: 'http://127.0.0.1:9222',
        defaultViewport: null
    });

    try {
        let pages = await browser.pages();
        let metaPage = pages.find(p => p.url().includes('business.facebook.com'));
        
        if (!metaPage) {
            console.log("Aba do Meta não encontrada, abrindo...");
            metaPage = await browser.newPage();
            await metaPage.goto("https://business.facebook.com/latest/home", { waitUntil: 'networkidle2', timeout: 60000 });
        } else {
            console.log("Trazendo a aba do Meta para frente...");
            await metaPage.bringToFront();
        }

        // Se houver um modal de "Done" de posts anteriores, vamos fechar
        const doneBtns = await metaPage.$$('::-p-text(Done)');
        for (let btn of doneBtns) {
             const isBtn = await metaPage.evaluate(el => el.tagName === 'DIV' && el.getAttribute('role') === 'button' || el.tagName === 'BUTTON', btn);
             if (isBtn) {
                 await btn.click();
                 await sleep(1000);
             }
        }

        for (let i = 0; i < records.length; i++) {
            const row = records[i];
            console.log(`\nProcessando [${i+1}/${records.length}]: ${row.tipo} - ${row.data} às ${row.hora}`);
            
            // Garantir que estamos na home
            if (!metaPage.url().includes('/latest/home')) {
                await metaPage.goto("https://business.facebook.com/latest/home", { waitUntil: 'networkidle2' });
                await sleep(5000);
            }

            // Seleciona "Create post" ou "Create reel"
            const type = row.tipo.trim().toLowerCase();
            let createBtns = [];
            if (type === 'reel' || type === 'video') {
                 createBtns = await metaPage.$$('::-p-text(Create reel)');
            } else {
                 createBtns = await metaPage.$$('::-p-text(Create post)');
            }
            
            if (createBtns.length > 0) {
                await createBtns[0].click();
                console.log("Aguardando página de criação abrir...");
                await sleep(8000);
            } else {
                console.log(`ERRO: Botão Create ${type} não encontrado.`);
                continue;
            }

            // Faz o upload da mídia
            console.log(`Enviando mídia: ${row.caminho_midia}`);
            let addPhotoBtn = await metaPage.$$('::-p-text(Add photo)');
            if (addPhotoBtn.length === 0) addPhotoBtn = await metaPage.$$('::-p-text(Add video)');
            if (addPhotoBtn.length === 0) addPhotoBtn = await metaPage.$$('::-p-text(Add photo/video)');
            
            if (addPhotoBtn.length > 0) {
                const fileChooserPromise = metaPage.waitForFileChooser({timeout: 5000}).catch(() => null);
                await addPhotoBtn[0].click();
                let fileChooser = await fileChooserPromise;
                
                if (!fileChooser) {
                    const uploadDesktop = await metaPage.$$('::-p-text(Upload from desktop)');
                    if (uploadDesktop.length > 0) {
                        const [fc] = await Promise.all([
                            metaPage.waitForFileChooser(),
                            uploadDesktop[0].click(),
                        ]);
                        fileChooser = fc;
                    }
                }
                
                if (fileChooser) {
                    await fileChooser.accept([row.caminho_midia]);
                    console.log("Upload em andamento. Aguardando 15s para garantir que o arquivo carregue...");
                    await sleep(15000); // Dar tempo do facebook processar (vídeos podem demorar mais)
                }
            } else {
                console.log("Botão de mídia não encontrado.");
            }

            // Texto (legenda)
            console.log("Inserindo legenda...");
            const textareas = await metaPage.$$('textarea');
            if (textareas.length > 0) {
                await textareas[0].type(row.texto);
            } else {
                const editableDiv = await metaPage.$('[contenteditable="true"]');
                if (editableDiv) {
                    await editableDiv.type(row.texto);
                }
            }

            // Agendamento
            console.log("Ativando agendamento (Set date and time)...");
            const scheduleToggle = await metaPage.$$('::-p-text(Set date and time)');
            if (scheduleToggle.length > 0) {
                await scheduleToggle[0].click();
                await sleep(2000);
            }

            // Inserir Data (no formato mm/dd/yyyy ou o aceito pela região do PC)
            console.log(`Inserindo data: ${row.data}`);
            const dateInputs = await metaPage.$$('input[placeholder*="yyyy"]');
            if (dateInputs.length > 0) {
                await dateInputs[0].click({clickCount: 3}); 
                await dateInputs[0].press('Backspace');
                await dateInputs[0].type(row.data);
                await metaPage.keyboard.press('Enter');
                await sleep(1000);
            }

            // Inserir Hora (e.g. 10:00 AM)
            console.log(`Inserindo hora: ${row.hora}`);
            const inputs = await metaPage.$$('input');
            let timeInput = null;
            for (let j = 0; j < inputs.length; j++) {
                const val = await metaPage.evaluate(el => el.value, inputs[j]);
                if (val && (val.includes('AM') || val.includes('PM'))) {
                    timeInput = inputs[j];
                    break;
                }
            }
            
            if (timeInput) {
                await timeInput.click({clickCount: 3});
                await timeInput.press('Backspace');
                await timeInput.type(row.hora);
                await metaPage.keyboard.press('Enter');
                await sleep(1000);
            }

            // Clicar em Schedule
            console.log("Clicando no botão Final (Schedule)...");
            const scheduleBtn = await metaPage.$$('::-p-text(Schedule)');
            let clicked = false;
            for (let btn of scheduleBtn) {
                const isButton = await metaPage.evaluate(el => el.tagName === 'DIV' && el.getAttribute('role') === 'button' || el.tagName === 'BUTTON', btn);
                if (isButton) {
                    await btn.click();
                    clicked = true;
                    break;
                }
            }
            if (!clicked && scheduleBtn.length > 0) {
                await scheduleBtn[scheduleBtn.length - 1].click();
            }

            console.log("Aguardando post ser salvo no Planner (10s)...");
            await sleep(10000);

            // Fechar o modal "You scheduled a post..." se ele aparecer
            const doneBtns2 = await metaPage.$$('::-p-text(Done)');
            for (let btn of doneBtns2) {
                 const isBtn = await metaPage.evaluate(el => el.tagName === 'DIV' && el.getAttribute('role') === 'button' || el.tagName === 'BUTTON', btn);
                 if (isBtn) {
                     await btn.click();
                     await sleep(2000);
                 }
            }
            
            console.log(`Post [${i+1}] agendado com sucesso!\n`);
        }

        console.log("Todos os posts foram agendados!");

    } catch (e) {
        console.error(e);
    } finally {
        await browser.disconnect();
    }
}

runInstagramBot();
