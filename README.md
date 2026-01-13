# To Do List - Python

Aplicativo simples para gerenciar tarefas diárias (Tkinter + JSON).

### Funcionalidades
- Adicionar tarefas
- Editar tarefas
- Remover tarefas
- Marcar/Desmarcar como concluída (duplo clique ou botão)
- Buscar tarefas por texto
- Persistência em `tasks.json`

## 🛠️ Requisitos
- **Python 3.7+** (recomendado da versão 3.8+)
- **Tkinter** (geralmente já incluído na instalação do Python)

> Dica: no Windows, instale o Python oficial (python.org) e verifique o Tkinter com:

```bash
python -c "import tkinter; print(tkinter.TkVersion)"
```

## 🚀 Como rodar
1. Abra um terminal na pasta do projeto
2. Execute:

```bash
python app.py
```

O aplicativo abrirá a interface gráfica; ao fechar, as tarefas são salvas automaticamente.

---

## 🚦 Uso rápido e atalhos
- **Adicionar:** digitar no campo superior e pressionar **Enter** ou clicar em **Adicionar**
- **Editar:** selecionar a tarefa e clicar em **Editar** ou usar o menu de contexto (botão direito)
- **Remover:** selecionar e clicar em **Remover** (há confirmação)
- **Alternar concluída:** duplo clique na tarefa ou usar **Marcar/Desmarcar**
- **Buscar:** digitar no campo de busca para filtrar em tempo real
- **Salvar:** clicar em **Salvar** para forçar gravação (o app salva ao fechar)

---

## 📁 Formato do arquivo `tasks.json`
Cada tarefa é um objeto com o formato (campos usados pelo `app.py`):

```json
{
  "id": "<uuid>",
  "title": "Texto da tarefa",
  "completed": false,
  "created_at": "2026-01-13T12:34:56.789012"
}
```

Exemplo (arquivo `tasks.json`):

```json
[
  {
    "id": "3b4f9f10-1234-4cbd-84b1-0a1e2d3f4abc",
    "title": "Comprar leite",
    "completed": false,
    "created_at": "2026-01-13T12:34:56.789012"
  }
]
```

Notas importantes:
- **Novas tarefas** são inseridas no **topo** da lista (ordem LIFO).
- A **busca** filtra tarefas pelo campo `title`, é **case-insensitive** e usa correspondência por **substring**.
- Ao **salvar**, se `tasks.json` existir, o conteúdo anterior é copiado para `tasks.json.bak` (backup simples).
- Ao **editar/remover/trocar status**, o aplicativo exige que uma tarefa esteja selecionada; caso contrário aparece a mensagem **"Selecione uma tarefa primeiro."**

---

## ⚠️ Tratamento de erros
- Falhas ao ler/gravar o arquivo disparam diálogos de erro com a informação do problema.
- Se `tasks.json` não existir, o app cria um novo automaticamente.
- Validações simples impedem títulos vazios ao adicionar/editar tarefas.

---

## 💡 Melhorias futuras
- Ordenação por data ou por status (concluídas/ativas)
- Registrar data de conclusão ao marcar como concluída
- Prioridade, etiquetas ou categorias
- Exportar/importar em CSV
- Interface mais rica (temas, ícones) ou empacotar com PyInstaller
- Testes unitários para operações de CRUD e I/O

---
