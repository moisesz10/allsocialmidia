const puppeteer = require('puppeteer-core');

// ==========================================
// CONFIGURAÇÕES DE SEGURANÇA E RATE LIMITS
// ==========================================
const DELAY_BETWEEN_DELETES = 15000; // 15 segundos entre deleções
const DELAY_BETWEEN_FOLLOWS_MIN = 1000; // 1 segundo (ultra rápido a pedido do usuário)
const DELAY_BETWEEN_FOLLOWS_MAX = 3000; // 3 segundos
const MAX_FOLLOWS_PER_RUN = 10000; // Alvo de 10 mil
const MAX_DELETES_PER_RUN = 50;

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));
const randomSleep = async (min, max) => {
    const time = Math.floor(Math.random() * (max - min + 1) + min);
    console.log(`Aguardando ${Math.round(time / 1000)} segundos por segurança...`);
    await sleep(time);
};

async function runMassAction() {
    const args = process.argv.slice(2);
    const action = args[0]; // 'delete' ou 'follow'
    const targetUsername = args[1]; // username alvo para follow (ex: neymarjr)

    if (!action || (action !== 'delete' && action !== 'follow')) {
        console.log("Uso: node mass_action.js <delete|follow> [targetUsername]");
        console.log("Ex: node mass_action.js delete");
        console.log("Ex: node mass_action.js follow neymarjr");
        return;
    }

    console.log(`Iniciando Bot Mass Action (${action})...`);

    const browser = await puppeteer.connect({
        browserURL: 'http://127.0.0.1:9222',
        defaultViewport: null
    });

    try {
        const pages = await browser.pages();
        let page = pages.find(p => p.url().includes('instagram.com'));
        
        if (!page) {
            console.log("Aba do Instagram não encontrada, abrindo nova aba...");
            page = await browser.newPage();
        } else {
            console.log("Trazendo a aba do Instagram para frente...");
            await page.bringToFront();
        }

        // Navega para a home do Instagram para garantir que está logado
        await page.goto('https://www.instagram.com/', { waitUntil: 'domcontentloaded', timeout: 60000 });
        await sleep(5000);

    if (action === 'delete') {
            await deletePosts(page);
        } else if (action === 'follow') {
            await followUsers(page, targetUsername);
        }

    } catch (e) {
        console.error("Erro inesperado:", e);
    } finally {
        await browser.disconnect();
        console.log("Desconectado do navegador.");
    }
}

async function deletePosts(page) {
    console.log("Acessando o próprio perfil para deletar posts...");
    
    // Pega o username da conta logada clicando no ícone do perfil na sidebar
    const profileLink = await page.$('a[href^="/"][href$="/"]:not([href="/"]):not([href="/explore/"]):not([href="/reels/"])');
    if (profileLink) {
        await profileLink.click();
    } else {
        console.log("Não foi possível encontrar o link do perfil. Certifique-se de estar logado.");
        return;
    }
    
    await sleep(5000);

    let deletedCount = 0;
    while (deletedCount < MAX_DELETES_PER_RUN) {
        // Encontra o primeiro post na grade
        const firstPost = await page.$('article a[href^="/p/"], article a[href^="/reel/"]');
        if (!firstPost) {
            console.log("Nenhum post encontrado. Todos os posts foram deletados!");
            break;
        }

        console.log(`Abrindo post ${deletedCount + 1}...`);
        await firstPost.click();
        await sleep(3000);

        try {
            // Clica nos 3 pontinhos (Mais opções)
            const optionsBtn = await page.$('svg[aria-label="More options"], svg[aria-label="Mais opções"]');
            if (optionsBtn) {
                // O svg está dentro de um botão ou div que é clicável
                const clickableParent = await optionsBtn.evaluateHandle(el => el.closest('button, [role="button"]'));
                await clickableParent.click();
            } else {
                console.log("Botão de opções não encontrado.");
                break;
            }
            await sleep(2000);

            // Clica em Deletar (texto em inglês ou português)
            const deleteOptions = await page.$$('div[role="dialog"] button, div[role="button"]');
            let clickedDelete = false;
            for (let btn of deleteOptions) {
                const text = await page.evaluate(el => el.textContent.toLowerCase(), btn);
                if (text === 'delete' || text === 'excluir') {
                    await btn.click();
                    clickedDelete = true;
                    break;
                }
            }

            if (!clickedDelete) {
                console.log("Opção de deletar não encontrada no menu.");
                break;
            }

            await sleep(2000);

            // Confirma a deleção
            const confirmBtns = await page.$$('div[role="dialog"] button');
            for (let btn of confirmBtns) {
                const text = await page.evaluate(el => el.textContent.toLowerCase(), btn);
                if (text === 'delete' || text === 'excluir') {
                    await btn.click();
                    break;
                }
            }

            console.log("Post deletado!");
            deletedCount++;
            
            // Espera a modal fechar e a página recarregar a grid
            await sleep(DELAY_BETWEEN_DELETES);
            
            // Recarrega a página para garantir que a grid atualizou
            await page.reload({ waitUntil: 'domcontentloaded' });
            await sleep(5000);

        } catch (err) {
            console.log("Erro ao tentar deletar o post:", err.message);
            break;
        }
    }
    
    console.log(`Processo de deleção finalizado. Total deletado: ${deletedCount}`);
}

async function followUsers(page, targetUsername) {
    if (targetUsername) {
        console.log(`Navegando para o perfil alvo: https://www.instagram.com/${targetUsername}/`);
        await page.goto(`https://www.instagram.com/${targetUsername}/`, { waitUntil: 'domcontentloaded' });
        await sleep(5000);

        // Procura o link de seguidores iterando por todos os links da página
        let followersLinkFound = false;
        const links = await page.$$('a');
        for (let link of links) {
            const href = await page.evaluate(el => el.getAttribute('href'), link);
            if (href && href.includes('/followers/')) {
                await link.click();
                followersLinkFound = true;
                break;
            }
        }

        if (!followersLinkFound) {
            const allElements = await page.$$('a, span, div');
            for (let el of allElements) {
                const text = await page.evaluate(e => e.textContent ? e.textContent.toLowerCase() : '', el);
                if (text.includes('seguidores') || text.includes('followers')) {
                    try {
                        await el.click();
                        followersLinkFound = true;
                        break;
                    } catch(e) {}
                }
            }
        }

        if (!followersLinkFound) {
            console.log("Link de seguidores não encontrado. Perfil privado ou username incorreto?");
            return;
        }
        
        console.log("Aguardando lista de seguidores abrir...");
        await sleep(5000);
    } else {
        console.log("Modo Aleatório Inteligente: Buscando perfis 100% ABERTOS via hashtag #estoicismo...");
        await page.goto('https://www.instagram.com/explore/tags/estoicismo/', { waitUntil: 'domcontentloaded' });
        await sleep(5000);

        // Clica no primeiro post da hashtag
        const firstPost = await page.$('article a[href^="/p/"], article a[href^="/reel/"]');
        if (firstPost) {
            await firstPost.click();
            await sleep(3000);
        } else {
            console.log("Nenhum post encontrado na hashtag.");
            return;
        }

        let followedCount = 0;
        let emptyPostsCount = 0;

        while (followedCount < MAX_FOLLOWS_PER_RUN) {
            let followedThisPost = false;
            // O post abre num dialog. Pegamos os botões dentro dele.
            const buttons = await page.$$('div[role="dialog"] header button, div[role="dialog"] button');
            
            for (let btn of buttons) {
                const text = await page.evaluate(el => el.textContent.trim(), btn);
                if (text === 'Follow' || text === 'Seguir') {
                    try {
                        await btn.click();
                        followedCount++;
                        followedThisPost = true;
                        console.log(`Seguiu autor do post (100% Aberto) [${followedCount}/${MAX_FOLLOWS_PER_RUN}]`);
                        await randomSleep(DELAY_BETWEEN_FOLLOWS_MIN, DELAY_BETWEEN_FOLLOWS_MAX);
                        break;
                    } catch (err) {}
                }
            }

            if (!followedThisPost) {
                // Pode já estar seguindo ou botão não encontrado
                emptyPostsCount++;
                await sleep(1000);
            } else {
                emptyPostsCount = 0;
            }

            // Se passarmos por 20 posts seguidos sem achar botão de seguir (ex: já segue todos ou erro), recarrega
            if (emptyPostsCount > 20) {
                console.log("Muitos posts repetidos ou já seguidos. Atualizando a página...");
                await page.reload({ waitUntil: 'domcontentloaded' });
                await sleep(5000);
                const retryPost = await page.$('article a[href^="/p/"], article a[href^="/reel/"]');
                if (retryPost) await retryPost.click();
                await sleep(3000);
                emptyPostsCount = 0;
                continue;
            }

            // Pressiona seta para a direita para ir para o próximo post
            await page.keyboard.press('ArrowRight');
            await sleep(2500); // Aguarda o próximo post carregar
        }
        
        console.log(`Processo de mass follow finalizado. Total seguido nesta execução: ${followedCount}`);
    }
}

runMassAction();
