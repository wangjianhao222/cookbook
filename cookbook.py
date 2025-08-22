import tkinter as tk
from tkinter import messagebox, scrolledtext, Toplevel, Label
import requests # 导入 requests 库，用于发起 HTTP 请求
import string # 导入 string 模块，用于获取字母表

class OnlineRecipeFetcher:
    """
    OnlineRecipeFetcher 类负责从 TheMealDB API 搜索和获取食谱数据。
    """
    def fetch_online_recipes(self, query):
        """
        从 TheMealDB API 搜索在线食谱 (按名称)。
        :param query: 搜索关键词。
        :return: 格式化后的在线食谱列表 (包含名称、食材、步骤、分类), 或空列表。
        """
        base_url = "https://www.themealdb.com/api/json/v1/1/search.php?s="
        try:
            # 限制超时时间，防止长时间等待
            response = requests.get(f"{base_url}{query}", timeout=10) 
            response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)
            data = response.json()
            
            online_recipes = []
            if data and data['meals']:
                for meal in data['meals']:
                    ingredients = []
                    # TheMealDB API 食材和量最多支持到 20 个
                    for i in range(1, 21): 
                        ingredient = meal.get(f'strIngredient{i}')
                        measure = meal.get(f'strMeasure{i}')
                        if ingredient and ingredient.strip():
                            # 格式化食材列表
                            ingredients.append(f"{measure.strip()} {ingredient.strip()}" if measure and measure.strip() else ingredient.strip())
                        else:
                            break # 如果没有更多食材，停止循环

                    online_recipes.append({
                        "name": meal.get('strMeal', '未知食谱'),
                        "ingredients": ingredients,
                        "instructions": meal.get('strInstructions', '无详细步骤。').replace('\r\n', '\n'),
                        "category": meal.get('strCategory', '未知分类'),
                    })
            return online_recipes
        except requests.exceptions.Timeout:
            messagebox.showerror("网络超时", "连接到食谱数据库超时。请检查您的网络连接并重试。")
            return []
        except requests.exceptions.ConnectionError:
            messagebox.showerror("网络错误", "无法连接到食谱数据库。请检查您的网络连接。")
            return []
        except requests.exceptions.RequestException as e:
            messagebox.showerror("API请求错误", f"从在线数据库获取食谱时出错: {e}")
            return []
        except Exception as e:
            messagebox.showerror("未知错误", f"处理在线食谱数据时发生未知错误: {e}")
            return []

    def fetch_online_recipes_by_first_letter(self, letter):
        """
        从 TheMealDB API 搜索在线食谱 (按首字母)。
        :param letter: 首字母 (单个字符)。
        :return: 格式化后的在线食谱列表, 或空列表。
        """
        base_url = "https://www.themealdb.com/api/json/v1/1/search.php?f="
        try:
            response = requests.get(f"{base_url}{letter}", timeout=10)
            response.raise_for_status()
            data = response.json()
            
            online_recipes = []
            if data and data['meals']:
                for meal in data['meals']:
                    ingredients = []
                    for i in range(1, 21):
                        ingredient = meal.get(f'strIngredient{i}')
                        measure = meal.get(f'strMeasure{i}')
                        if ingredient and ingredient.strip():
                            ingredients.append(f"{measure.strip()} {ingredient.strip()}" if measure and measure.strip() else ingredient.strip())
                        else:
                            break

                    online_recipes.append({
                        "name": meal.get('strMeal', '未知食谱'),
                        "ingredients": ingredients,
                        "instructions": meal.get('strInstructions', '无详细步骤。').replace('\r\n', '\n'),
                        "category": meal.get('strCategory', '未知分类'),
                    })
            return online_recipes
        except requests.exceptions.Timeout:
            # messagebox.showerror("网络超时", f"连接到食谱数据库超时 (字母: {letter})。") # 频繁弹窗可能不好
            return []
        except requests.exceptions.ConnectionError:
            # messagebox.showerror("网络错误", f"无法连接到食谱数据库 (字母: {letter})。")
            return []
        except requests.exceptions.RequestException as e:
            print(f"从在线数据库获取食谱时出错 (字母: {letter}): {e}") # 打印到控制台而不是弹窗
            return []
        except Exception as e:
            print(f"处理在线食谱数据时发生未知错误 (字母: {letter}): {e}")
            return []

class CookbookApp:
    """
    CookbookApp 类负责构建和管理基于在线 API 的食谱大全图形用户界面。
    """
    def __init__(self, master):
        """
        初始化食谱应用界面。
        :param master: Tkinter 根窗口。
        """
        self.master = master
        master.title("在线食谱大全")
        master.geometry("900x700") # 设置初始窗口大小
        master.resizable(True, True) # 允许窗口缩放

        self.online_fetcher = OnlineRecipeFetcher()
        self.current_recipe_data = None # 用于存储当前选中的食谱完整数据

        # 设置主框架
        self.main_frame = tk.Frame(master, padx=10, pady=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 顶部搜索/功能区域
        self.top_controls_frame = tk.Frame(self.main_frame)
        self.top_controls_frame.pack(pady=10)

        tk.Label(self.top_controls_frame, text="输入食谱名称或关键词:", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(self.top_controls_frame, width=30, font=("Arial", 12))
        self.search_entry.pack(side=tk.LEFT, padx=10)
        self.search_entry.bind("<Return>", self.perform_search_event) # 绑定回车键

        self.search_btn = tk.Button(self.top_controls_frame, text="搜索食谱", command=self.perform_search, width=12, height=2, bg="#FFC107", fg="black", font=("Arial", 10, "bold"))
        self.search_btn.pack(side=tk.LEFT, padx=5)

        self.show_all_btn = tk.Button(self.top_controls_frame, text="显示所有食谱", command=self.show_all_recipes_from_api, width=15, height=2, bg="#2196F3", fg="white", font=("Arial", 10, "bold"))
        self.show_all_btn.pack(side=tk.LEFT, padx=5)


        # 内容显示区域
        self.content_frame = tk.Frame(self.main_frame, bd=2, relief="groove", padx=10, pady=10)
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # 初始提示信息
        self.show_initial_message()

        self.loading_window = None # 用于加载提示的窗口

    def clear_content_frame(self):
        """
        清除内容显示区域的所有小部件。
        """
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_initial_message(self):
        """
        显示初始欢迎和使用提示。
        """
        self.clear_content_frame()
        tk.Label(self.content_frame, text="欢迎使用在线食谱大全！", font=("Arial", 16, "bold"), fg="#333").pack(pady=20)
        tk.Label(self.content_frame, text="在上方搜索框输入关键词进行搜索，\n或者点击“显示所有食谱”查看来自 TheMealDB 的大量食谱。", font=("Arial", 12), wraplength=500).pack(pady=10)
        tk.Label(self.content_frame, text="数据来自 TheMealDB 公开 API。", font=("Arial", 10), fg="#666").pack(pady=5)


    def show_loading_message(self, message="正在加载中..."):
        """
        显示一个加载提示窗口。
        """
        if self.loading_window:
            self.loading_window.destroy()

        self.loading_window = Toplevel(self.master)
        self.loading_window.title("加载中")
        self.loading_window.transient(self.master) # 让加载窗口浮动在主窗口之上
        self.loading_window.grab_set() # 阻止与主窗口的交互

        # 计算居中位置
        main_x = self.master.winfo_x()
        main_y = self.master.winfo_y()
        main_width = self.master.winfo_width()
        main_height = self.master.winfo_height()

        loading_width = 250
        loading_height = 100
        x = main_x + (main_width // 2) - (loading_width // 2)
        y = main_y + (main_height // 2) - (loading_height // 2)
        self.loading_window.geometry(f"{loading_width}x{loading_height}+{x}+{y}")
        self.loading_window.resizable(False, False)

        Label(self.loading_window, text=message, font=("Arial", 12)).pack(expand=True)
        self.master.update_idletasks() # 强制更新界面

    def hide_loading_message(self):
        """
        隐藏加载提示窗口。
        """
        if self.loading_window:
            self.loading_window.grab_release() # 释放对主窗口的阻止
            self.loading_window.destroy()
            self.loading_window = None


    def show_recipe_list(self, recipe_list, title="在线搜索结果"):
        """
        显示搜索结果列表。
        :param recipe_list: 要显示的食谱数据字典列表。
        :param title: 列表标题。
        """
        self.clear_content_frame()
        tk.Label(self.content_frame, text=title, font=("Arial", 14, "bold")).pack(pady=10)

        self.recipe_listbox = tk.Listbox(self.content_frame, height=20, width=60, font=("Arial", 12), selectmode=tk.SINGLE)
        self.recipe_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 添加滚动条
        scrollbar = tk.Scrollbar(self.content_frame, orient="vertical", command=self.recipe_listbox.yview)
        scrollbar.pack(side=tk.LEFT, fill="y")
        self.recipe_listbox.config(yscrollcommand=scrollbar.set)

        self.display_recipes_data = {} # 存储 {食谱名称: 完整食谱数据}
        if recipe_list:
            # 按食谱名称排序
            sorted_recipes = sorted(recipe_list, key=lambda x: x.get('name', ''))
            for recipe_data in sorted_recipes:
                name = recipe_data.get("name")
                if name:
                    self.recipe_listbox.insert(tk.END, name)
                    self.display_recipes_data[name] = recipe_data
        
        self.recipe_listbox.bind("<<ListboxSelect>>", self.on_recipe_select)

        # 详情显示区域
        self.detail_frame = tk.Frame(self.content_frame, bd=1, relief="solid", padx=10, pady=10)
        self.detail_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(self.detail_frame, text="食谱详情", font=("Arial", 14, "bold")).pack(pady=5)
        self.recipe_details_text = scrolledtext.ScrolledText(self.detail_frame, width=50, height=20, font=("Arial", 12), wrap=tk.WORD, state=tk.DISABLED)
        self.recipe_details_text.pack(fill=tk.BOTH, expand=True)

    def on_recipe_select(self, event):
        """
        当食谱列表中的项目被选中时，显示其详细信息。
        :param event: 事件对象。
        """
        selected_indices = self.recipe_listbox.curselection()
        if not selected_indices:
            self.current_recipe_data = None
            self.recipe_details_text.config(state=tk.NORMAL)
            self.recipe_details_text.delete("1.0", tk.END)
            self.recipe_details_text.config(state=tk.DISABLED)
            return

        index = selected_indices[0]
        selected_recipe_name = self.recipe_listbox.get(index)
        recipe_data = self.display_recipes_data.get(selected_recipe_name)
        
        self.current_recipe_data = recipe_data # 存储当前选中食谱的完整数据

        self.recipe_details_text.config(state=tk.NORMAL) # 允许编辑
        self.recipe_details_text.delete("1.0", tk.END) # 清空旧内容

        if recipe_data:
            details = f"食谱名称: {selected_recipe_name}\n"
            details += f"分类: {recipe_data.get('category', '无')}\n\n"
            details += "食材:\n"
            # 确保食材列表不为空才显示
            if recipe_data["ingredients"]:
                for ingredient in recipe_data["ingredients"]:
                    details += f"- {ingredient}\n"
            else:
                details += "- 无可用食材信息。\n"

            details += "\n烹饪步骤:\n"
            details += recipe_data["instructions"]
            self.recipe_details_text.insert(tk.END, details)
        self.recipe_details_text.config(state=tk.DISABLED) # 再次禁用编辑

    def perform_search_event(self, event):
        """
        绑定回车键的搜索事件。
        """
        self.perform_search()

    def perform_search(self):
        """
        执行在线搜索 (按名称) 并显示结果。
        """
        query = self.search_entry.get().strip()
        if not query:
            self.show_initial_message() # 如果搜索框为空，显示初始提示
            messagebox.showwarning("搜索提示", "请输入搜索关键词。")
            return

        self.show_loading_message("正在搜索食谱...")
        self.master.update_idletasks() # 强制更新界面以显示加载消息

        online_results = self.online_fetcher.fetch_online_recipes(query)
        
        self.hide_loading_message() # 隐藏加载提示

        if online_results:
            self.show_recipe_list(online_results, title=f"在线搜索结果 '{query}'")
            messagebox.showinfo("搜索完成", f"在线找到 {len(online_results)} 个匹配食谱。")
        else:
            self.show_recipe_list([]) # 清空列表
            messagebox.showinfo("搜索结果", f"未找到与 '{query}' 匹配的在线食谱。")

    def show_all_recipes_from_api(self):
        """
        从 API 获取所有食谱 (通过遍历首字母) 并显示。
        """
        self.show_loading_message("正在获取所有食谱，这可能需要一些时间...")
        self.master.update_idletasks() # 强制更新界面以显示加载消息

        all_recipes = {} # 使用字典来存储食谱，以便按名称去重
        for letter in string.ascii_lowercase: # 遍历所有小写字母
            recipes_by_letter = self.online_fetcher.fetch_online_recipes_by_first_letter(letter)
            for recipe in recipes_by_letter:
                all_recipes[recipe['name']] = recipe # 以食谱名称为键，确保唯一性
        
        # 将字典的值转换为列表，以便传递给 show_recipe_list
        unique_recipes_list = list(all_recipes.values())

        self.hide_loading_message() # 隐藏加载提示

        if unique_recipes_list:
            self.show_recipe_list(unique_recipes_list, title=f"所有在线食谱 ({len(unique_recipes_list)} 个)")
            messagebox.showinfo("加载完成", f"已从在线数据库获取并显示 {len(unique_recipes_list)} 个食谱。")
        else:
            self.show_recipe_list([])
            messagebox.showerror("加载失败", "未能从在线数据库获取任何食谱，请检查网络连接。")

if __name__ == "__main__":
    root = tk.Tk()
    app = CookbookApp(root)
    root.mainloop()
