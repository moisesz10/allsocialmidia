import csv
import json

def generate():
    posts = []
    with open('cronograma_comunidade.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            posts.append(row)
            
    js_code = """
async function runBot(posts) {
    console.log("🤖 Iniciando Robô da Comunidade...");
    for (let i = 0; i < posts.length; i++) {
        let p = posts[i];
        let isFirstDay = (i < 2);
        
        console.log(`⏳ Processando post ${i+1}/${posts.length}...`);
        
        // Clica na caixa de texto
        let inputBox = document.querySelector('div#contenteditable-root');
        if (!inputBox) {
            let createBox = document.querySelector('ytd-backstage-post-creation-renderer');
            if (createBox) createBox.click();
            await new Promise(r => setTimeout(r, 1000));
            inputBox = document.querySelector('div#contenteditable-root');
        }
        
        if (!inputBox) {
            console.error("❌ Não achou a caixa de texto!");
            return;
        }
        
        inputBox.focus();
        // Limpa e digita
        inputBox.innerText = p.texto;
        inputBox.dispatchEvent(new InputEvent('input', {bubbles: true}));
        await new Promise(r => setTimeout(r, 1000));
        
        if (isFirstDay) {
            console.log("🚀 Publicando agora!");
            let postBtn = document.querySelector('ytd-button-renderer#submit-button button');
            if (postBtn) postBtn.click();
            await new Promise(r => setTimeout(r, 5000));
        } else {
            console.log(`⏰ Agendando para ${p.data} às ${p.hora}...`);
            let schedBtn = document.querySelector('ytd-button-renderer#schedule-button button');
            if (schedBtn) schedBtn.click();
            await new Promise(r => setTimeout(r, 1500));
            
            // Preenche data
            let datePicker = document.querySelector('ytcp-text-dropdown-trigger#datepicker-trigger');
            if (datePicker) {
                datePicker.click();
                await new Promise(r => setTimeout(r, 500));
                let dateInput = document.querySelector('tp-yt-paper-input input');
                if (dateInput) {
                    dateInput.value = p.data;
                    dateInput.dispatchEvent(new Event('input', {bubbles: true}));
                }
            }
            
            // Preenche hora
            let timePicker = document.querySelector('ytcp-text-dropdown-trigger#time-of-day-trigger');
            if (timePicker) {
                timePicker.click();
                await new Promise(r => setTimeout(r, 500));
                let timeInput = document.querySelectorAll('tp-yt-paper-input input')[1];
                if (timeInput) {
                    timeInput.value = p.hora;
                    timeInput.dispatchEvent(new Event('input', {bubbles: true}));
                }
            }
            
            // Clica agendar modal
            let modalBtn = document.querySelector('ytcp-button#submit-button');
            if (modalBtn) modalBtn.click();
            await new Promise(r => setTimeout(r, 5000));
        }
        
        console.log(`✅ Post ${i+1} finalizado!`);
    }
    console.log("🎉 Todas as postagens foram concluídas!");
}

const postsData = """ + json.dumps(posts, ensure_ascii=False, indent=4) + """;

runBot(postsData);
"""
    with open('script_console.js', 'w', encoding='utf-8') as f:
        f.write(js_code)
    print("Script JS gerado em script_console.js")

if __name__ == '__main__':
    generate()
