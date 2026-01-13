"""
To Do List Application - Versão Definitiva
==========================================
Aplicação completa de gerenciamento de tarefas com interface gráfica moderna.

Recursos principais:
- CRUD completo de tarefas (Create, Read, Update, Delete)
- Sistema de busca em tempo real
- Ordenação por data ou ordem alfabética
- Estatísticas em tempo real
- Persistência automática em JSON
- Interface responsiva e intuitiva
- Atalhos de teclado
- Menu de contexto
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import uuid
from datetime import datetime
from typing import Optional, Tuple, List, Dict

DATA_FILE = os.path.join(os.path.dirname(__file__), "tasks.json")


class TodoApp(tk.Tk):
    """Classe principal que gerencia a aplicação To Do List."""
    
    def __init__(self):
        """Inicializa a aplicação e seus componentes."""
        super().__init__()
        self._configure_window()
        
        self.tasks: List[Dict] = [] 
        self.filtered_tasks: List[Dict] = []
        self.sort_mode = 'date'

        self._build_ui()
        self.load_tasks()
        self.refresh_listbox()
        self._update_stats()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _configure_window(self):
        """
        Configura as propriedades da janela principal.
        Define título, dimensões e comportamento de redimensionamento.
        """
        self.title("To Do List - Python")
        self.geometry("700x500")
        self.resizable(True, True)
        self.minsize(600, 400)

    def _build_ui(self):
        """
        Constrói toda a interface gráfica chamando métodos especializados.
        Organiza a UI em seções: topo, estatísticas, meio, rodapé e menu.
        """
        self._build_top_section()
        self._build_stats_section()
        self._build_middle_section()
        self._build_bottom_section()
        self._build_context_menu()

    def _build_top_section(self):
        """
        Cria a seção superior da interface.
        Contém: campo de entrada de nova tarefa, botão adicionar e campo de busca.
        """
        top = ttk.Frame(self)
        top.pack(side=tk.TOP, fill=tk.X, padx=10, pady=8)

        # Campo para digitar nova tarefa
        self.entry_task = ttk.Entry(top, font=('Arial', 10))
        self.entry_task.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        self.entry_task.bind("<Return>", lambda _: self.add_task())
        self.entry_task.focus()

        # Botão para adicionar a tarefa
        btn_add = ttk.Button(top, text="➕ Adicionar", command=self.add_task)
        btn_add.pack(side=tk.LEFT)

        # Campo de busca
        lbl_search = ttk.Label(top, text="🔎")
        lbl_search.pack(side=tk.LEFT, padx=(12, 4))
        
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *a: self._on_search_changed())
        
        entry_search = ttk.Entry(top, textvariable=self.search_var, width=25)
        entry_search.pack(side=tk.LEFT)

    def _build_stats_section(self):
        """
        Cria a barra de estatísticas.
        Exibe contadores: total de tarefas, pendentes e concluídas.
        Inclui botão de ordenação.
        """
        stats_frame = ttk.Frame(self)
        stats_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(0, 8))
        
        self.stats_label = ttk.Label(
            stats_frame, 
            text="Total: 0 | Pendentes: 0 | Concluídas: 0",
            foreground="gray"
        )
        self.stats_label.pack(side=tk.LEFT)
        
        self.sort_btn = ttk.Button(
            stats_frame, 
            text="🔽 Ordenar por Data", 
            command=self._toggle_sort,
            width=20
        )
        self.sort_btn.pack(side=tk.RIGHT)

    def _build_middle_section(self):
        """
        Cria a seção central com a listbox de tarefas.
        Configura eventos de teclado e mouse para interação.
        Atalhos: Duplo clique (marcar), Delete (remover), Enter (editar), Botão direito (menu).
        """
        mid = ttk.Frame(self)
        mid.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 8))

        self.listbox = tk.Listbox(
            mid, 
            height=15, 
            activestyle='none',
            font=('Arial', 10),
            selectmode=tk.SINGLE
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configuração de eventos
        self.listbox.bind('<Double-1>', lambda _: self.toggle_complete())
        self.listbox.bind('<Button-3>', lambda e: self._show_context_menu(e))
        self.listbox.bind('<Delete>', lambda _: self.delete_task())
        self.listbox.bind('<Return>', lambda _: self.edit_task())

        scroll = ttk.Scrollbar(mid, orient=tk.VERTICAL, command=self.listbox.yview)
        scroll.pack(side=tk.LEFT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scroll.set)

    def _build_bottom_section(self):
        """
        Cria a seção inferior com botões de ação.
        Botões: Editar, Remover, Marcar/Desmarcar, Limpar Concluídas e Salvar.
        """
        bot = ttk.Frame(self)
        bot.pack(fill=tk.X, padx=10, pady=(0, 10))

        btn_edit = ttk.Button(bot, text="✏️ Editar", command=self.edit_task)
        btn_edit.pack(side=tk.LEFT, padx=(0, 4))

        btn_delete = ttk.Button(bot, text="🗑️ Remover", command=self.delete_task)
        btn_delete.pack(side=tk.LEFT, padx=(0, 4))

        btn_toggle = ttk.Button(bot, text="✓ Marcar/Desmarcar", command=self.toggle_complete)
        btn_toggle.pack(side=tk.LEFT, padx=(0, 4))

        btn_clear = ttk.Button(bot, text="🧹 Limpar Concluídas", command=self.clear_completed)
        btn_clear.pack(side=tk.LEFT)

        btn_save = ttk.Button(bot, text="💾 Salvar", command=self._manual_save)
        btn_save.pack(side=tk.RIGHT)

    def _build_context_menu(self):
        """
        Cria o menu de contexto (botão direito do mouse).
        Opções: Editar, Remover e Marcar/Desmarcar.
        """
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="✏️ Editar", command=self.edit_task)
        self.menu.add_command(label="🗑️ Remover", command=self.delete_task)
        self.menu.add_separator()
        self.menu.add_command(label="✓ Marcar/Desmarcar", command=self.toggle_complete)

    def _show_context_menu(self, event):
        """
        Exibe o menu de contexto no local do clique.
        Seleciona automaticamente o item clicado antes de mostrar o menu.
        """
        try:
            self.listbox.selection_clear(0, tk.END)
            idx = self.listbox.nearest(event.y)
            self.listbox.selection_set(idx)
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def _on_search_changed(self):
        """
        Callback executado quando o texto de busca é modificado.
        Atualiza automaticamente a lista filtrada de tarefas.
        """
        self.refresh_listbox()

    def _toggle_sort(self):
        """
        Alterna o modo de ordenação entre data e alfabético.
        Atualiza o texto do botão e reordena a lista de tarefas.
        """
        if self.sort_mode == 'date':
            self.sort_mode = 'alpha'
            self.sort_btn.config(text="🔽 Ordenar A-Z")
        else:
            self.sort_mode = 'date'
            self.sort_btn.config(text="🔽 Ordenar por Data")
        self.refresh_listbox()

    def _update_stats(self):
        """
        Atualiza a barra de estatísticas com contadores atualizados.
        Calcula: total de tarefas, tarefas pendentes e tarefas concluídas.
        """
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t.get('completed', False))
        pending = total - completed
        
        self.stats_label.config(
            text=f"Total: {total} | Pendentes: {pending} | Concluídas: {completed}"
        )

    def _sort_tasks(self, tasks: List[Dict]) -> List[Dict]:
        """
        Ordena a lista de tarefas de acordo com o modo selecionado.
        
        Modos disponíveis:
        - 'alpha': Ordem alfabética (A-Z)
        - 'date': Ordem cronológica (mais recentes primeiro)
        """
        if self.sort_mode == 'alpha':
            return sorted(tasks, key=lambda t: t['title'].lower())
        else:
            return sorted(tasks, key=lambda t: t.get('created_at', ''), reverse=True)

    def load_tasks(self):
        """
        Carrega as tarefas do arquivo JSON.
        Se o arquivo não existir, cria um novo.
        Trata erros de arquivo corrompido ou inexistente.
        """
        if not os.path.exists(DATA_FILE):
            self.tasks = []
            self.save_tasks()
            return
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                self.tasks = json.load(f)
        except json.JSONDecodeError:
            messagebox.showerror("Erro", "Arquivo de tarefas corrompido. Criando novo arquivo.")
            self.tasks = []
            self.save_tasks()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar tarefas: {e}")
            self.tasks = []

    def save_tasks(self):
        """
        Salva as tarefas no arquivo JSON.
        Cria um backup (.bak) antes de sobrescrever o arquivo existente.
        Garante a integridade dos dados em caso de falha.
        """
        try:
            if os.path.exists(DATA_FILE):
                backup = DATA_FILE + ".bak"
                try:
                    with open(DATA_FILE, 'r', encoding='utf-8') as f:
                        with open(backup, 'w', encoding='utf-8') as b:
                            b.write(f.read())
                except:
                    pass
            
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar tarefas: {e}")

    def _manual_save(self):
        """
        Executa salvamento manual das tarefas.
        Exibe mensagem de confirmação ao usuário.
        """
        self.save_tasks()
        messagebox.showinfo("Sucesso", "Tarefas salvas com sucesso!")

    def refresh_listbox(self):
        """
        Atualiza a visualização da listbox de tarefas.
        Aplica filtro de busca, ordenação e formatação visual.
        Tarefas concluídas são exibidas em cinza com símbolo ✓.
        """
        q = self.search_var.get().strip().lower()
        
        if q:
            self.filtered_tasks = [t for t in self.tasks if q in t['title'].lower()]
        else:
            self.filtered_tasks = list(self.tasks)

        self.filtered_tasks = self._sort_tasks(self.filtered_tasks)

        self.listbox.delete(0, tk.END)
        for t in self.filtered_tasks:
            prefix = "✓ " if t.get('completed') else "☐ "
            self.listbox.insert(tk.END, f"{prefix}{t['title']}")
            
            if t.get('completed'):
                idx = self.listbox.size() - 1
                self.listbox.itemconfig(idx, foreground='gray')

    def add_task(self):
        """
        Adiciona uma nova tarefa à lista.
        Cria um objeto de tarefa com ID único, título, status e data.
        Valida se o campo não está vazio antes de adicionar.
        Salva automaticamente e atualiza a interface.
        """
        title = self.entry_task.get().strip()
        if not title:
            messagebox.showwarning("Aviso", "Digite uma tarefa antes de adicionar.")
            return
        
        task = {
            'id': str(uuid.uuid4()),
            'title': title,
            'completed': False,
            'created_at': datetime.now().isoformat()
        }
        
        self.tasks.insert(0, task)
        self.entry_task.delete(0, tk.END)
        self.save_tasks()
        self.refresh_listbox()
        self._update_stats()
        self.entry_task.focus()

    def _get_selected_task(self) -> Optional[Tuple[int, Dict]]:
        """
        Obtém a tarefa atualmente selecionada na listbox.
        Busca a tarefa correspondente na lista principal usando o ID.
        
        Returns:
            Tupla (índice, tarefa) ou None se nenhuma tarefa estiver selecionada.
        """
        sel = self.listbox.curselection()
        if not sel:
            return None
        
        idx = sel[0]
        task = self.filtered_tasks[idx]
        
        for i, t in enumerate(self.tasks):
            if t['id'] == task['id']:
                return i, t
        return None

    def edit_task(self):
        """
        Permite editar o texto de uma tarefa existente.
        Abre diálogo para o usuário inserir o novo texto.
        Valida se o novo texto não está vazio.
        Registra a data de atualização e salva as alterações.
        """
        res = self._get_selected_task()
        if not res:
            messagebox.showinfo("Info", "Selecione uma tarefa primeiro.")
            return
        
        idx, task = res
        new = simpledialog.askstring(
            "Editar tarefa", 
            "Novo texto:", 
            initialvalue=task['title'],
            parent=self
        )
        
        if new is None:
            return
        
        new = new.strip()
        if new == "":
            messagebox.showwarning("Aviso", "Tarefa não pode ficar vazia.")
            return
        
        self.tasks[idx]['title'] = new
        self.tasks[idx]['updated_at'] = datetime.now().isoformat()
        self.save_tasks()
        self.refresh_listbox()

    def delete_task(self):
        """
        Remove uma tarefa da lista após confirmação.
        Solicita confirmação do usuário antes de deletar.
        Atualiza estatísticas após a remoção.
        """
        res = self._get_selected_task()
        if not res:
            messagebox.showinfo("Info", "Selecione uma tarefa primeiro.")
            return
        
        idx, task = res
        if messagebox.askyesno("Confirmar", f"Remover tarefa '{task['title']}'?"):
            self.tasks.pop(idx)
            self.save_tasks()
            self.refresh_listbox()
            self._update_stats()

    def toggle_complete(self):
        """
        Alterna o status de completo/incompleto da tarefa.
        Pode ser acionado por: duplo clique, botão ou menu de contexto.
        Registra a data de atualização e salva as alterações.
        """
        res = self._get_selected_task()
        if not res:
            return
        
        idx, task = res
        self.tasks[idx]['completed'] = not self.tasks[idx].get('completed', False)
        self.tasks[idx]['updated_at'] = datetime.now().isoformat()
        self.save_tasks()
        self.refresh_listbox()
        self._update_stats()

    def clear_completed(self):
        """
        Remove todas as tarefas marcadas como concluídas.
        Solicita confirmação antes de realizar a operação em lote.
        Exibe mensagem de sucesso informando quantas tarefas foram removidas.
        """
        completed_count = sum(1 for t in self.tasks if t.get('completed', False))
        
        if completed_count == 0:
            messagebox.showinfo("Info", "Não há tarefas concluídas para remover.")
            return
        
        if messagebox.askyesno(
            "Confirmar", 
            f"Remover {completed_count} tarefa(s) concluída(s)?"
        ):
            self.tasks = [t for t in self.tasks if not t.get('completed', False)]
            self.save_tasks()
            self.refresh_listbox()
            self._update_stats()
            messagebox.showinfo("Sucesso", f"{completed_count} tarefa(s) removida(s)!")

    def on_close(self):
        """
        Manipula o fechamento da janela.
        Garante que todas as tarefas sejam salvas antes de encerrar.
        """
        self.save_tasks()
        self.destroy()


if __name__ == '__main__':
    app = TodoApp()
    app.mainloop()