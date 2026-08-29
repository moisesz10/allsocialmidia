
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

const postsData = [
    {
        "data": "29/08/2026",
        "hora": "11:30",
        "texto": "Quanta energia você gastou hoje se preocupando com coisas que não pode controlar? O trânsito, a reação dos outros, o clima ou o passado... Tudo isso está fora do seu domínio. 🛑\n\nEpicteto nos lembrava que a verdadeira paz de espírito começa no momento em que dividimos o mundo em duas categorias: o que depende de nós e o que não depende.\n\nSeu foco, suas ações e suas reações são sua total responsabilidade. O resto é apenas ruído externo. 🎯\n\nQual foi a última coisa fora do seu controle que você decidiu simplesmente soltar e deixar ir?"
    },
    {
        "data": "29/08/2026",
        "hora": "19:00",
        "texto": "Você não é imortal. Pode parecer óbvio, mas quantas vezes agimos como se tivéssemos todo o tempo do mundo pela frente? ⏳\n\nOs imperadores romanos mantinham servos ao seu lado com a única função de sussurrar: \"Memento Mori\" — lembre-se de que você vai morrer. Não para causar medo, mas para trazer clareza e urgência à vida.\n\nSaber que seu tempo é finito transforma a forma como você trata o dia de hoje. A raiva perde a força, a procrastinação some e o que realmente importa ganha vida. 💡\n\nSe hoje fosse o seu último dia no planeta, o que você faria de diferente agora mesmo?"
    },
    {
        "data": "30/08/2026",
        "hora": "11:30",
        "texto": "E se você parasse de desejar que as coisas fossem diferentes e começasse a amar exatamente o que acontece com você? 🌪️\n\n\"Amor Fati\" é o conceito estoico de não apenas suportar o destino, mas abraçá-lo plenamente. Se os seus planos falharam hoje, esse novo caminho é a sua oportunidade perfeita para praticar a resiliência.\n\nO fogo não reclama do vento forte; ele usa a ventania para crescer ainda mais intenso. 🔥\n\nQual evento difícil do seu passado você hoje consegue enxergar como uma lição valiosa?"
    },
    {
        "data": "30/08/2026",
        "hora": "19:00",
        "texto": "Sabe aquele grande problema que está tirando o seu sono esta semana? Ele pode ser a sua maior oportunidade de crescimento. 🪨\n\nMarco Aurélio escreveu que \"o impedimento à ação avança a ação. O que fica no caminho torna-se o caminho.\" Se há um obstáculo, há uma chance de treinar a paciência, a coragem ou a criatividade.\n\nNão peça por uma vida sem desafios. Peça por forças e sabedoria para superar os desafios inevitáveis. 💪\n\nQual desafio atual da sua vida você pode transformar em uma oportunidade de aprendizado hoje?"
    },
    {
        "data": "31/08/2026",
        "hora": "11:30",
        "texto": "Chega de teorizar sobre quem você quer ser. É hora de agir. 🏛️\n\nEpicteto costumava dizer: \"Não explique a sua filosofia, encarne-a.\" De nada adianta ler dezenas de livros sobre estoicismo se suas atitudes diárias continuam impulsivas e impacientes.\n\nSuas escolhas em momentos de pressão dizem muito mais sobre seu caráter do que qualquer citação bonita que você compartilha. ⚖️\n\nQual pequena atitude prática você vai tomar hoje para demonstrar a sua filosofia na vida real?"
    },
    {
        "data": "31/08/2026",
        "hora": "19:00",
        "texto": "Nós temos dois ouvidos e apenas uma boca para que possamos ouvir o dobro do que falamos. 🤫\n\nNo mundo moderno, todos estão desesperados para emitir opiniões, gritar e provar que estão certos. O estoico prefere a calma do silêncio e o poder da observação atenta.\n\nGuardar suas palavras não é sinal de fraqueza, é puro domínio próprio. Quem muito fala, pouco reflete. 🧠\n\nEm qual situação recente você percebeu que ficar em silêncio foi a sua melhor decisão?"
    },
    {
        "data": "01/09/2026",
        "hora": "11:30",
        "texto": "A sua mente é como uma fortaleza inexpugnável. Nada do lado de fora pode invadir a sua paz a menos que você abra os portões. 🏰\n\nPessoas vão te criticar, planos vão falhar e imprevistos vão acontecer. Mas a sua reação interna continua sendo 100% sua.\n\nQuando você constrói essa \"Cidadela Interior\", o caos do mundo externo perde a capacidade de abalar as suas estruturas. 🛡️\n\nO que você faz diariamente para proteger a sua paz mental do excesso de ruído externo?"
    },
    {
        "data": "01/09/2026",
        "hora": "19:00",
        "texto": "A raiva é um surto temporário de loucura. Ela destrói muito mais quem a sente do que aquele contra quem é dirigida. 💥\n\nSêneca dedicou um livro inteiro ao tema da raiva, mostrando que ela nasce da expectativa irreal de que o mundo deveria ser perfeito e as pessoas sempre agradáveis.\n\nSentir raiva é como tomar veneno esperando que a outra pessoa morra. O antídoto estoico é a pausa: respire antes de reagir. 🧘‍♂️\n\nQual técnica você usa para não perder a cabeça quando alguém te provoca?"
    },
    {
        "data": "02/09/2026",
        "hora": "11:30",
        "texto": "Quando foi a última vez que você se colocou intencionalmente em uma situação desconfortável? 🌧️\n\nSêneca aconselhava a tirar alguns dias no mês para comer comida simples, vestir roupas humildes e encarar o desconforto. O objetivo? Perceber que o seu pior receio não é tão terrível assim.\n\nQuem treina no tempo de paz não entra em pânico durante a guerra. A disciplina de verdade nasce no desconforto voluntário. 🧱\n\nDe qual pequeno luxo você estaria disposto a abrir mão por uma semana para treinar sua resiliência?"
    },
    {
        "data": "02/09/2026",
        "hora": "19:00",
        "texto": "Como foi o seu dia hoje? Você viveu de acordo com os seus valores ou se deixou levar pelo piloto automático? 📖\n\nAntes de dormir, o filósofo Sêneca fazia um exame sincero de consciência. Ele se perguntava: Que hábito ruim eu venci hoje? Em que melhorei? Como posso fazer melhor amanhã?\n\nEscrever e refletir sobre suas atitudes não é um mero diário, é uma ferramenta de lapidação da alma. 🖋️\n\nSe você fizesse uma avaliação honesta das suas atitudes de hoje, qual nota daria a si mesmo?"
    },
    {
        "data": "03/09/2026",
        "hora": "11:30",
        "texto": "As coisas e os fatos não são bons nem ruins por si sós. É o julgamento que você faz deles que cria a sua dor. 🧠\n\nSe alguém cancela um compromisso com você, é possível encarar isso como uma desfeita ou como um tempo livre inesperado para focar em si mesmo. O evento é exatamente o mesmo, a percepção muda tudo.\n\nMude a sua narrativa interna e você mudará instantaneamente a sua experiência da realidade. 👁️\n\nQue situação chata da sua semana ganharia um novo significado se você mudasse apenas a sua perspectiva?"
    },
    {
        "data": "03/09/2026",
        "hora": "19:00",
        "texto": "Diga-me com quem andas e te direi quem és. Os estoicos já alertavam sobre isso há mais de dois mil anos. 👥\n\nEpicteto chamava a atenção para o perigo de se associar a pessoas pessimistas, fofoqueiras ou sem ambição moral. A mentalidade dos outros é contagiosa, para o bem ou para o mal.\n\nCercar-se de pessoas que buscam a virtude e a evolução constante te obriga a subir o seu próprio nível. 📈\n\nAs pessoas com quem você mais convive hoje estão te empurrando para frente ou te puxando para baixo?"
    },
    {
        "data": "04/09/2026",
        "hora": "11:30",
        "texto": "A forma como você começa as suas primeiras horas define o tom de todo o seu dia. 🌅\n\nMarco Aurélio começava a manhã lembrando a si mesmo: \"Hoje me encontrarei com pessoas medrosas, ingratas e arrogantes. Mas nada disso pode me ferir, pois conheço a natureza do Bem.\"\n\nAntecipar mentalmente as dificuldades não é ser pessimista, é estar preparado para não ser pego de surpresa pelo caos. 🛡️\n\nQual é a primeira coisa que você faz ou pensa logo ao acordar pela manhã?"
    },
    {
        "data": "04/09/2026",
        "hora": "19:00",
        "texto": "Rico não é aquele que acumula muito, mas aquele que precisa de pouco para viver bem. 💎\n\nO mundo moderno vende a ideia de que precisamos de mais um carro, mais uma roupa ou mais aprovação para sermos felizes. Isso é uma corrida sem fim.\n\nA verdadeira liberdade financeira e emocional vem da capacidade de limitar nossos desejos e valorizar o que já está presente. ⚖️\n\nQual foi a última coisa que você comprou achando que traria felicidade, mas percebeu que não mudou nada na sua paz?"
    },
    {
        "data": "05/09/2026",
        "hora": "11:30",
        "texto": "A ansiedade vive no futuro. O arrependimento vive no passado. A vida real só acontece no momento presente. ⏳\n\nSêneca afirmava que sofremos muito mais na imaginação do que na realidade. Gastamos uma energia preciosa temendo cenários catastróficos que nunca vão se concretizar.\n\nTraga a sua mente de volta para o agora. Este segundo é o único momento sobre o qual você tem algum controle. 🧘‍♂️\n\nO que a sua mente está tentando antecipar hoje que você deveria simplesmente entregar ao tempo?"
    },
    {
        "data": "05/09/2026",
        "hora": "19:00",
        "texto": "Nenhum ser humano é uma ilha isolada. Nós fomos feitos para colaborar uns com os outros. 🤝\n\nOs estoicos usavam o termo *Sympatheia* para descrever a interconexão de tudo no universo. Fazer o bem ao outro é fazer o bem a si mesmo; prejudicar o próximo é prejudicar a si próprio.\n\nO que prejudica a colmeia, prejudica a abelha. A virtude não é egoísta, ela se expressa na utilidade para o mundo. 🐝\n\nQue pequeno ato de bondade ou ajuda você pode praticar por alguém hoje, sem esperar nada em troca?"
    },
    {
        "data": "06/09/2026",
        "hora": "11:30",
        "texto": "A motivação é uma emoção passageira. A disciplina é o compromisso inabalável com o seu dever. 🏋️‍♂️\n\nHaverá dias em que você não terá vontade de treinar, de estudar ou de trabalhar. O homem comum espera a vontade chegar; o estoico faz o que precisa ser feito assim mesmo.\n\nVença a batalha contra a preguiça logo nos primeiros minutos do dia. Essa é a vitória mais importante. 🔥\n\nO que você sabe que precisa fazer hoje, mas está adiando por pura falta de \"motivação\"?"
    },
    {
        "data": "06/09/2026",
        "hora": "19:00",
        "texto": "O que os outros pensam ou dizem sobre você não é da sua conta. 🤷‍♂️\n\nSe alguém fala mal de você, lembre-se da lição de Epicteto: essa pessoa fala com base no que ela julga correto. Se ela está errada, ela é quem sofre o dano da própria ignorância.\n\nAlém disso, se a crítica for verdadeira, corrija-se. Se for falsa, por que se importar com uma mentira? 💎\n\nComo você costuma reagir quando descobre que alguém fez uma crítica injusta a seu respeito?"
    },
    {
        "data": "07/09/2026",
        "hora": "11:30",
        "texto": "Compare-se apenas com quem você foi ontem, nunca com quem outra pessoa é hoje. 📐\n\nOlhar para o palco dos outros enquanto você vivencia os seus bastidores é a receita perfeita para a frustração. O caminho estoico exige foco total na sua própria jornada.\n\nO único parâmetro real de progresso é o quanto você evoluiu no domínio das suas próprias fraquezas. 🏆\n\nEm qual área da sua vida você sente que mais evoluiu quando olha para quem você era há um ano?"
    },
    {
        "data": "07/09/2026",
        "hora": "19:00",
        "texto": "A verdadeira liberdade não é poder fazer tudo o que se tem vontade, mas ser mestre das próprias vontades. 🕊️\n\nAlguém que vive escravo da raiva, do medo, da aprovação alheia ou dos vícios nunca será livre, mesmo que viva em um palácio.\n\nA autêntica liberdade começa quando você aprende a dizer \"não\" aos impulsos da mente e escolhe agir com a razão. ⚖️\n\nO que ainda tem o poder de controlar os seus pensamentos ou atitudes no seu dia a dia?"
    }
];

runBot(postsData);
