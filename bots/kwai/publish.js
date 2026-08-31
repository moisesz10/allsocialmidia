const fs = require('fs');
const puppeteer = require('puppeteer-core');
const { parse } = require('csv-parse/sync');

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function runKwaiBot() {
    console.log("Iniciando Bot do Kwai (Kwai Creator Center)...");

    const args = process.argv.slice(2);
    const csvPath = args.length > 0 ? args[0] : 'data/cronograma_kwai.csv';
    
    if (!fs.existsSync(csvPath)) {
        console.error(`Erro: Arquivo ${csvPath} não encontrado.`);
        return;
    }
    
    console.log(`Lendo arquivo CSV: ${csvPath}`);
    const csvData = fs.readFileSync(csvPath, 'utf8');
    const records = parse(csvData, {
        columns: true,
        skip_empty_lines: true
    });

    console.log(`Foram encontrados ${records.length} vídeos para enviar.`);

    const browser = await puppeteer.connect({
        browserURL: 'http://127.0.0.1:9222',
        defaultViewport: null
    });

    try {
        let pages = await browser.pages();
        let kwaiPage = pages.find(p => p.url().includes('kwai.com'));
        
        if (!kwaiPage) {
            console.log("Aba do Kwai não encontrada, abrindo página principal...");
            kwaiPage = await browser.newPage();
            await kwaiPage.goto("https://cp.kwai.com/", { waitUntil: 'domcontentloaded', timeout: 60000 });
        } else {
            console.log("Trazendo a aba do Kwai para frente...");
            await kwaiPage.bringToFront();
        }
        
        await sleep(5000); // Aguardar o carregamento inicial

        for (let i = 0; i < records.length; i++) {
            const row = records[i];
            console.log(`\nProcessando [${i+1}/${records.length}]: ${row.tipo} - Data: ${row.data} às ${row.hora}`);
            
            try {
                // Apenas garante que estamos num domínio do kwai
                if (!kwaiPage.url().includes('kwai.com')) {
                    await kwaiPage.goto("https://cp.kwai.com/", { waitUntil: 'domcontentloaded', timeout: 60000 });
                    await sleep(5000);
                }

                // 1. Upload do vídeo
                console.log(`Enviando vídeo: ${row.caminho_midia}`);
                const fileInput = await kwaiPage.$('input[type="file"]');
                if (fileInput) {
                    await fileInput.uploadFile(row.caminho_midia);
                    console.log("Upload em andamento. Aguardando 15s para garantir que o arquivo carregue...");
                    await sleep(15000); 
                } else {
                    console.log("ERRO: Input de upload de vídeo não encontrado. Verifique se o seletor está correto.");
                    continue;
                }

                // 2. Inserir legenda
                console.log("Inserindo legenda...");
                // No Kwai, geralmente é uma div contenteditable
                const fallbackInput = await kwaiPage.$('[contenteditable="true"]');
                if (fallbackInput) {
                    await fallbackInput.click({clickCount: 3});
                    await fallbackInput.press('Backspace');
                    await fallbackInput.type(row.texto);
                } else {
                    console.log("ERRO: Campo de texto da legenda não encontrado.");
                }
                
                await sleep(2000);

                // 3. Postar imediatamente
                // O Kwai Creator não tem agendamento padronizado em todas as contas, geralmente clica-se direto em publicar.
                console.log("Procurando botão de Publicar/Postar...");
                const publishBtn = await kwaiPage.$$('::-p-text(Publicar)');
                if (publishBtn.length > 0) {
                    await publishBtn[0].click();
                } else {
                    const postBtn = await kwaiPage.$$('::-p-text(Post)');
                    if (postBtn.length > 0) {
                        await postBtn[0].click();
                    } else {
                        const postarBtn = await kwaiPage.$$('::-p-text(Postar)');
                        if (postarBtn.length > 0) {
                            await postarBtn[0].click();
                        } else {
                            console.log("ERRO: Botão de publicação não encontrado.");
                        }
                    }
                }

                console.log("Aguardando post ser salvo (10s)...");
                await sleep(10000);
                
                console.log(`Vídeo [${i+1}] enviado com sucesso!\n`);
                
                // Recarrega a página para publicar o próximo vídeo limpo
                await kwaiPage.reload({ waitUntil: 'domcontentloaded', timeout: 60000 }).catch(() => {});
                await sleep(5000);

            } catch (err) {
                console.error(`Erro ao processar vídeo [${i+1}]:`, err.message);
                console.log("Tentando recarregar a tela para o próximo vídeo...");
                await kwaiPage.reload({ waitUntil: 'domcontentloaded' }).catch(() => {});
                await sleep(5000);
            }
        }

        console.log("Automação do Kwai concluída!");

    } catch (e) {
        console.error(e);
    } finally {
        await browser.disconnect();
    }
}

runKwaiBot();
