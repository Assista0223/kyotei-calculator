import flet as ft
from typing import List, Dict, Tuple
import math
import pyperclip


class OddsCalculator:
    def __init__(self):
        self.total_amount = 0
        self.main_target_return = 0
        self.suppression_target_return = 0
        self.aim_target_return = 0
        
    def calculate_bet_amount(self, odds: float, total_amount: float, target_return_rate: float) -> int:
        if odds <= 0 or target_return_rate <= 0:
            return 0
        required_return = total_amount * target_return_rate
        bet_amount = math.ceil(required_return / odds / 100) * 100
        return bet_amount
    
    def calculate_synthetic_odds(self, bets_data: List[Dict]) -> float:
        """合成オッズを計算（掛け金の比率を考慮した加重平均）"""
        if not bets_data:
            return 0
        
        total_bet = sum(bet.get('bet_amount', 0) for bet in bets_data)
        if total_bet == 0:
            return 0
        
        # 各舟券の確率を掛け金の比率で重み付け
        weighted_probability = 0
        for bet in bets_data:
            bet_amount = bet.get('bet_amount', 0)
            odds = bet.get('odds', 0)
            if bet_amount > 0 and odds > 0:
                # この舟券の掛け金比率
                weight = bet_amount / total_bet
                # 1/オッズが的中確率の推定値
                probability = 1 / odds
                weighted_probability += weight * probability
        
        if weighted_probability > 0:
            # 合成オッズ = 1 / 加重平均確率
            return 1 / weighted_probability
        return 0
    
    def calculate_minimum_bet_for_target(self, odds: float, target_return: float) -> int:
        """目標払戻金額に到達するための最小掛け金を計算"""
        if odds <= 0:
            return 0
        return math.ceil(target_return / odds / 100) * 100
    
    def calculate_distribution_strict(self, bets_data: List[Dict]) -> Tuple[List[Dict], str]:
        if not bets_data:
            return [], "賭け対象が設定されていません"
        
        results = []
        total_required = 0
        warning_message = None
        
        for bet in bets_data:
            min_bet = self.calculate_bet_amount(
                bet['odds'], 
                self.total_amount,
                bet['target_return']
            )
            total_required += min_bet
            
            # 総掛け金が不足していても、とりあえず最小掛け金で計算
            actual_bet = min_bet
            if total_required > self.total_amount:
                # 不足分を案分して調整（最低100円は確保）
                actual_bet = max(100, int(self.total_amount / len(bets_data) / 100) * 100)
            
            results.append({
                'name': bet['name'],
                'category': bet['category'],
                'odds': bet['odds'],
                'bet_amount': actual_bet,
                'expected_return': actual_bet * bet['odds'],
                'return_rate': (actual_bet * bet['odds']) / self.total_amount if self.total_amount > 0 else 0,
                'target_return': bet['target_return'],
                'meets_target': (actual_bet * bet['odds']) >= (self.total_amount * bet['target_return']),
                'min_bet_for_target': self.calculate_minimum_bet_for_target(
                    bet['odds'], 
                    self.total_amount * bet['target_return']
                )
            })
        
        # 警告メッセージを設定（エラーとして返さない）
        if total_required > self.total_amount:
            warning_message = f"⚠️ 目標達成には総掛け金が不足しています。必要額: {total_required:,}円"
        
        if total_required < self.total_amount:
            surplus = self.total_amount - total_required
            weights = []
            for bet in bets_data:
                weight = 1.0 / bet['target_return'] if bet['target_return'] > 0 else 1.0
                weights.append(weight)
            
            total_weight = sum(weights)
            
            for i, result in enumerate(results):
                if total_weight > 0:
                    additional = int((surplus * weights[i] / total_weight) / 100) * 100
                    result['bet_amount'] += additional
                    result['expected_return'] = result['bet_amount'] * result['odds']
                    result['return_rate'] = result['expected_return'] / self.total_amount if self.total_amount > 0 else 0
                    result['meets_target'] = result['return_rate'] >= result['target_return']
                    result['min_bet_for_target'] = self.calculate_minimum_bet_for_target(
                        result['odds'],
                        self.total_amount * result['target_return']
                    )
        
        return results, warning_message


def main(page: ft.Page):
    page.title = "KYOTEI FUND CALCULATOR"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0a0a0a"
    page.padding = 0
    page.scroll = ft.ScrollMode.AUTO
    page.window_min_width = 320
    page.fonts = {
        "NotoSans": "https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500;700&display=swap"
    }
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary="#6366f1",
            primary_container="#4f46e5",
            secondary="#10b981",
            secondary_container="#059669",
            surface="#1a1a1a",
            surface_variant="#2a2a2a",
            background="#0a0a0a",
            error="#ef4444",
            on_primary="#ffffff",
            on_surface="#f8fafc",
            outline="#374151",
        )
    )
    
    calculator = OddsCalculator()
    stored_results = []
    
    # カスタムカラー
    GRADIENT_PRIMARY = ft.LinearGradient(
        colors=["#6366f1", "#8b5cf6"],
        begin=ft.alignment.top_left,
        end=ft.alignment.bottom_right,
    )
    
    GRADIENT_SUCCESS = ft.LinearGradient(
        colors=["#10b981", "#06b6d4"],
        begin=ft.alignment.top_left,
        end=ft.alignment.bottom_right,
    )
    
    GRADIENT_DANGER = ft.LinearGradient(
        colors=["#ef4444", "#f97316"],
        begin=ft.alignment.top_left,
        end=ft.alignment.bottom_right,
    )
    
    def create_glass_card(content, padding=20, elevation=4):
        return ft.Container(
            content=content,
            padding=padding,
            margin=10,
            bgcolor="#1a1a1a80",
            border=ft.border.all(1, "#374151"),
            border_radius=16,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=elevation * 4,
                color="#00000040",
                offset=ft.Offset(0, elevation),
            ),
        )
    
    def create_modern_button(text, on_click, gradient, icon=None, expand=False):
        content = [ft.Text(text, color="white", weight=ft.FontWeight.W_600, size=14)]
        if icon:
            content.insert(0, ft.Icon(icon, color="white", size=18))
        
        return ft.Container(
            content=ft.Row(
                content,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8,
            ),
            padding=ft.padding.symmetric(vertical=12, horizontal=20),
            border_radius=12,
            gradient=gradient,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=8,
                color="#00000030",
                offset=ft.Offset(0, 2),
            ),
            on_click=on_click,
            expand=expand,
        )
    
    def create_input_field(label, value="", keyboard_type=ft.KeyboardType.TEXT, expand=True):
        return ft.TextField(
            label=label,
            value=value,
            keyboard_type=keyboard_type,
            expand=expand,
            filled=True,
            bgcolor="#2a2a2a",
            border_color="#374151",
            focused_border_color="#6366f1",
            label_style=ft.TextStyle(color="#9ca3af"),
            text_style=ft.TextStyle(color="#f8fafc"),
            cursor_color="#6366f1",
            border_radius=8,
        )
    
    # 本物のAdMob広告バナー（テストID使用）
    admob_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3940256099942544"
                crossorigin="anonymous"></script>
        <style>
            body {
                margin: 0;
                padding: 8px;
                background-color: #0f172a;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            }
            .ad-container {
                background-color: #1a1a1a;
                border: 1px solid #374151;
                border-radius: 8px;
                padding: 8px;
                text-align: center;
            }
            .ad-label {
                font-size: 10px;
                color: #9ca3af;
                margin-bottom: 8px;
            }
            .adsbygoogle {
                display: block;
            }
        </style>
    </head>
    <body>
        <div class="ad-container">
            <div class="ad-label">広告</div>
            <!-- Google AdMob テストバナー広告 -->
            <ins class="adsbygoogle"
                 style="display:block"
                 data-ad-client="ca-pub-3940256099942544"
                 data-ad-slot="6300978111"
                 data-ad-format="auto"
                 data-full-width-responsive="true"></ins>
            <script>
                 (adsbygoogle = window.adsbygoogle || []).push({});
            </script>
        </div>
    </body>
    </html>
    """
    
    # AdMob広告エリア（実装用テンプレート）
    real_admob_banner = ft.Container(
        content=ft.Column([
            ft.Text("広告", size=10, color="#9ca3af", text_align=ft.TextAlign.CENTER),
            ft.Container(height=4),
            ft.Container(
                content=ft.Row([
                    ft.Icon("ads_click", color="#ff6b6b", size=18),
                    ft.Column([
                        ft.Text("📱 REAL ADMOB INTEGRATION READY", size=11, weight=ft.FontWeight.BOLD, color="#ff6b6b"),
                        ft.Text("テストID: ca-pub-3940256099942544 | APK化で収益化開始", size=9, color="#9ca3af"),
                    ], spacing=1, expand=True),
                    ft.Container(
                        content=ft.Text("AD", size=8, color="white", weight=ft.FontWeight.BOLD),
                        bgcolor="#ff6b6b",
                        padding=ft.padding.symmetric(horizontal=6, vertical=2),
                        border_radius=4,
                    ),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
                padding=ft.padding.symmetric(horizontal=16, vertical=10),
                bgcolor="#1a1a1a",
                border=ft.border.all(1, "#ff6b6b40"),
                border_radius=8,
                width=float("inf"),
            ),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
        padding=ft.padding.symmetric(horizontal=10, vertical=8),
        bgcolor="#0f172a",
        border=ft.border.only(bottom=ft.border.BorderSide(1, "#334155")),
        width=float("inf"),
    )
    
    # ヘッダー
    header = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon("waves", color="#6366f1", size=32),
                ft.Text(
                    "KYOTEI FUND CALCULATOR",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color="#f8fafc",
                ),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=12),
            ft.Text(
                "競艇資金配分最適化ツール",
                size=14,
                color="#9ca3af",
                text_align=ft.TextAlign.CENTER,
            ),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
        gradient=GRADIENT_PRIMARY,
        padding=24,
        border_radius=ft.border_radius.only(bottom_left=20, bottom_right=20),
    )
    
    # 基本設定
    total_amount_field = create_input_field("総掛け金（円）", "10000", ft.KeyboardType.NUMBER)
    main_return_field = create_input_field("本線倍率", "1.5", ft.KeyboardType.NUMBER)
    suppression_return_field = create_input_field("抑え倍率", "1.2", ft.KeyboardType.NUMBER)
    aim_return_field = create_input_field("狙い倍率", "2.0", ft.KeyboardType.NUMBER)
    
    settings_card = create_glass_card(
        ft.Column([
            ft.Row([
                ft.Icon("settings", color="#6366f1", size=20),
                ft.Text("基本設定", size=18, weight=ft.FontWeight.W_600, color="#f8fafc"),
            ], spacing=8),
            ft.Container(height=12),
            ft.ResponsiveRow([
                ft.Column(col={"sm": 12, "md": 3}, controls=[total_amount_field]),
                ft.Column(col={"sm": 12, "md": 3}, controls=[main_return_field]),
                ft.Column(col={"sm": 12, "md": 3}, controls=[suppression_return_field]),
                ft.Column(col={"sm": 12, "md": 3}, controls=[aim_return_field]),
            ]),
        ])
    )
    
    # 各カテゴリの入力エリア
    main_bets = ft.Column(scroll=ft.ScrollMode.AUTO)
    suppression_bets = ft.Column(scroll=ft.ScrollMode.AUTO)
    aim_bets = ft.Column(scroll=ft.ScrollMode.AUTO)
    
    def add_bet_row(category: str, container: ft.Column):
        bet_row = ft.Container(
            content=ft.ResponsiveRow([
                ft.Column(
                    col={"xs": 5, "sm": 5},
                    controls=[create_input_field("舟券", expand=False)]
                ),
                ft.Column(
                    col={"xs": 5, "sm": 5},
                    controls=[create_input_field("オッズ", keyboard_type=ft.KeyboardType.NUMBER, expand=False)]
                ),
                ft.Column(
                    col={"xs": 2, "sm": 2},
                    controls=[
                        ft.IconButton(
                            icon="delete",
                            icon_color="#ef4444",
                            icon_size=18,
                            on_click=lambda e: remove_bet_row(container, bet_row),
                            tooltip="削除",
                        )
                    ]
                ),
            ]),
            padding=8,
            margin=ft.margin.symmetric(vertical=4),
            bgcolor="#2a2a2a40",
            border_radius=8,
        )
        container.controls.append(bet_row)
        page.update()
    
    def remove_bet_row(container: ft.Column, row: ft.Container):
        container.controls.remove(row)
        page.update()
    
    def create_category_section(title, container, color, multiplier_text):
        return create_glass_card(
            ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Row([
                            ft.Icon("bookmark", color=color, size=20),
                            ft.Text(title, size=16, weight=ft.FontWeight.W_600, color="#f8fafc"),
                        ], spacing=8),
                        expand=True,
                    ),
                    ft.Text(f"倍率: {multiplier_text}", size=12, color="#9ca3af"),
                    ft.Container(
                        content=ft.Icon("add", color="white", size=16),
                        bgcolor=color,
                        border_radius=20,
                        padding=8,
                        on_click=lambda e: add_bet_row(title.lower(), container),
                        tooltip=f"{title}を追加",
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=8),
                container,
            ])
        )
    
    main_section = create_category_section("本線", main_bets, "#6366f1", "1.5")
    suppression_section = create_category_section("抑え", suppression_bets, "#10b981", "1.2")
    aim_section = create_category_section("狙い", aim_bets, "#f59e0b", "2.0")
    
    # 結果表示
    results_container = ft.Column(scroll=ft.ScrollMode.AUTO)
    summary_text = ft.Text("計算結果待ち...", size=16, weight=ft.FontWeight.W_600, color="#9ca3af")
    synthetic_odds_text = ft.Text("", size=14, color="#9ca3af")
    min_bet_info_text = ft.Text("", size=12, color="#9ca3af")
    
    def update_section_multipliers():
        # 各セクションの倍率表示を更新
        main_section.content.controls[0].controls[1].value = f"倍率: {main_return_field.value}"
        suppression_section.content.controls[0].controls[1].value = f"倍率: {suppression_return_field.value}"
        aim_section.content.controls[0].controls[1].value = f"倍率: {aim_return_field.value}"
        page.update()
    
    main_return_field.on_change = lambda e: update_section_multipliers()
    suppression_return_field.on_change = lambda e: update_section_multipliers()
    aim_return_field.on_change = lambda e: update_section_multipliers()
    
    def copy_results(e):
        if not stored_results:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("コピーする結果がありません", color="white"),
                bgcolor="#ef4444"
            )
            page.snack_bar.open = True
            page.update()
            return
        
        copy_text = "🏁 KYOTEI FUND CALCULATOR RESULTS\n"
        copy_text += "=" * 50 + "\n"
        copy_text += f"💰 総掛け金: {calculator.total_amount:,.0f}円\n\n"
        
        for result in stored_results:
            status = "✅" if result['meets_target'] else "❌"
            copy_text += f"{status} {result['category']}: {result['name']}\n"
            copy_text += f"   📊 オッズ: {result['odds']:.1f}\n"
            copy_text += f"   💵 掛け金: {result['bet_amount']:,}円\n"
            copy_text += f"   💎 払戻金: {result['expected_return']:,.0f}円\n"
            copy_text += f"   📈 回収率: {result['return_rate']*100:.1f}%\n\n"
        
        total_bet = sum(r['bet_amount'] for r in stored_results)
        copy_text += "=" * 50 + "\n"
        copy_text += f"📊 合計掛け金: {total_bet:,}円\n"
        copy_text += "🔗 Generated by KYOTEI FUND CALCULATOR"
        
        try:
            pyperclip.copy(copy_text)
            page.snack_bar = ft.SnackBar(
                content=ft.Text("📋 結果をクリップボードにコピーしました！", color="white"),
                bgcolor="#10b981"
            )
            page.snack_bar.open = True
            page.update()
        except:
            page.clipboard.set_data(ft.ClipboardData(copy_text))
            page.snack_bar = ft.SnackBar(
                content=ft.Text("📋 結果をクリップボードにコピーしました！", color="white"),
                bgcolor="#10b981"
            )
            page.snack_bar.open = True
            page.update()
    
    def reset_all(e):
        total_amount_field.value = "10000"
        main_return_field.value = "1.5"
        suppression_return_field.value = "1.2"
        aim_return_field.value = "2.0"
        
        main_bets.controls.clear()
        suppression_bets.controls.clear()
        aim_bets.controls.clear()
        
        for _ in range(2):
            add_bet_row("main", main_bets)
            add_bet_row("suppression", suppression_bets)
            add_bet_row("aim", aim_bets)
        
        results_container.controls.clear()
        stored_results.clear()
        summary_text.value = "計算結果待ち..."
        summary_text.color = "#9ca3af"
        synthetic_odds_text.value = ""
        min_bet_info_text.value = ""
        update_section_multipliers()
        page.update()
    
    def adjust_bet_amount(idx: int, amount: int):
        if idx < len(stored_results):
            result = stored_results[idx]
            new_bet = max(100, result['bet_amount'] + amount)
            
            current_total = sum(r['bet_amount'] for r in stored_results)
            new_total = current_total - result['bet_amount'] + new_bet
            
            if new_total > calculator.total_amount:
                excess = new_total - calculator.total_amount
                for i, other in enumerate(stored_results):
                    if i != idx and other['bet_amount'] > 100:
                        reduction = min(excess, other['bet_amount'] - 100)
                        other['bet_amount'] -= reduction
                        other['expected_return'] = other['bet_amount'] * other['odds']
                        other['return_rate'] = other['expected_return'] / calculator.total_amount
                        other['meets_target'] = other['return_rate'] >= other['target_return']
                        excess -= reduction
                        if excess <= 0:
                            break
            
            result['bet_amount'] = new_bet
            result['expected_return'] = new_bet * result['odds']
            result['return_rate'] = result['expected_return'] / calculator.total_amount
            result['meets_target'] = result['return_rate'] >= result['target_return']
            result['min_bet_for_target'] = calculator.calculate_minimum_bet_for_target(
                result['odds'],
                calculator.total_amount * result['target_return']
            )
            
            display_results()
    
    def display_results():
        results_container.controls.clear()
        total_bet = 0
        category_min_bets = {'本線': [], '抑え': [], '狙い': []}
        
        for idx, result in enumerate(stored_results):
            total_bet += result['bet_amount']
            if result['category'] in category_min_bets:
                category_min_bets[result['category']].append(result.get('min_bet_for_target', 0))
            
            # カテゴリー別の色設定
            category_colors = {
                "本線": "#6366f1",
                "抑え": "#10b981", 
                "狙い": "#f59e0b"
            }
            
            card_color = category_colors.get(result['category'], "#6366f1")
            text_color = "#ef4444" if not result['meets_target'] else "#f8fafc"
            status_icon = "error" if not result['meets_target'] else "check_circle"
            status_color = "#ef4444" if not result['meets_target'] else "#10b981"
            
            result_card = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Container(
                            content=ft.Row([
                                ft.Icon("bookmark", color=card_color, size=16),
                                ft.Text(f"{result['category']}: {result['name']}", 
                                       weight=ft.FontWeight.W_600, color=text_color, size=14),
                            ], spacing=6),
                            expand=True,
                        ),
                        ft.Row([
                            ft.Icon(status_icon, color=status_color, size=16),
                            ft.Text(f"{result['odds']:.1f}倍", color="#9ca3af", size=12),
                        ], spacing=4),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    
                    ft.Container(height=8),
                    
                    ft.Row([
                        ft.Container(
                            content=ft.Column([
                                ft.Text("掛金", size=10, color="#9ca3af"),
                                ft.Text(f"{result['bet_amount']:,}円", color=text_color, weight=ft.FontWeight.W_500),
                                ft.Text(
                                    f"必要: {result.get('min_bet_for_target', 0):,}円" if result.get('min_bet_for_target', 0) > result['bet_amount']
                                    else f"✓ 達成済", 
                                    size=9, 
                                    color="#ef4444" if result.get('min_bet_for_target', 0) > result['bet_amount'] else "#10b981"
                                ),
                            ], spacing=2),
                            padding=8,
                            bgcolor="#374151" if result.get('min_bet_for_target', 0) <= result['bet_amount'] else "#7f1d1d40",
                            border_radius=6,
                            on_click=lambda e, i=idx: adjust_bet_amount(i, -100),
                            tooltip="クリックで-100円",
                            expand=True,
                        ),
                        
                        ft.Container(
                            content=ft.Column([
                                ft.Text("払戻", size=10, color="#9ca3af"),
                                ft.Text(f"{result['expected_return']:,.0f}円", color=text_color, weight=ft.FontWeight.W_500),
                            ], spacing=2),
                            padding=8,
                            bgcolor="#374151",
                            border_radius=6,
                            on_click=lambda e, i=idx: adjust_bet_amount(i, 100),
                            tooltip="クリックで+100円",
                            expand=True,
                        ),
                        
                        ft.Container(
                            content=ft.Column([
                                ft.Text("回収率", size=10, color="#9ca3af"),
                                ft.Text(f"{result['return_rate']*100:.1f}%", color=text_color, weight=ft.FontWeight.W_500),
                            ], spacing=2),
                            padding=8,
                            bgcolor="#374151" if result['meets_target'] else "#7f1d1d",
                            border_radius=6,
                            expand=True,
                        ),
                    ], spacing=8),
                ]),
                padding=16,
                margin=ft.margin.symmetric(vertical=4),
                bgcolor="#1a1a1a",
                border=ft.border.all(1, card_color + "40"),
                border_radius=12,
                shadow=ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=4,
                    color="#00000020",
                    offset=ft.Offset(0, 2),
                ),
            )
            results_container.controls.append(result_card)
        
        summary_text.value = f"💰 合計掛け金: {total_bet:,}円 / 設定: {calculator.total_amount:,.0f}円"
        summary_text.color = "#10b981" if total_bet <= calculator.total_amount else "#ef4444"
        
        # 合成オッズを計算（常に表示）
        if stored_results:
            synthetic_odds = calculator.calculate_synthetic_odds(stored_results)
            if synthetic_odds > 0:
                # 実際の合成オッズを表示
                synthetic_odds_text.value = f"📊 合成オッズ: {synthetic_odds:.2f}倍"
                synthetic_odds_text.color = "#10b981"
            else:
                # 計算できない場合
                synthetic_odds_text.value = "📊 合成オッズ: 計算不可"
                synthetic_odds_text.color = "#ef4444"
        else:
            synthetic_odds_text.value = ""
        
        # 各カテゴリの最小掛け金情報と達成可能性を判定
        min_bet_info = []
        total_min_required = 0
        category_achievable = {'本線': False, '抑え': False, '狙い': False}
        
        for category, min_bets in category_min_bets.items():
            if min_bets:
                total_min = sum(min_bets)
                total_min_required += total_min
                if total_min > 0:
                    min_bet_info.append(f"{category}: {total_min:,}円")
                    # 現在の掛け金で達成可能か判定
                    current_category_bet = sum(r['bet_amount'] for r in stored_results if r['category'] == category)
                    if current_category_bet >= total_min:
                        category_achievable[category] = True
        
        # 目標達成可能性を判定して表示
        if total_min_required > 0:
            if total_min_required <= calculator.total_amount:
                # 理論的に達成可能
                if total_min_required <= total_bet:
                    # 現在の配分で達成済み
                    min_bet_info_text.value = f"✅ 目標達成可能 - 必要最小金額: {' / '.join(min_bet_info)} (合計: {total_min_required:,}円)"
                    min_bet_info_text.color = "#10b981"
                else:
                    # 達成可能だが現在の配分では未達成
                    min_bet_info_text.value = f"⚠️ 目標達成には調整が必要 - 必要最小金額: {' / '.join(min_bet_info)} (合計: {total_min_required:,}円)"
                    min_bet_info_text.color = "#f59e0b"
            else:
                # 総掛け金が不足で達成不可能
                shortage = total_min_required - calculator.total_amount
                min_bet_info_text.value = f"❌ 目標達成不可能 - 必要金額: {total_min_required:,}円 (不足: {shortage:,}円)"
                min_bet_info_text.color = "#ef4444"
        else:
            min_bet_info_text.value = ""
        
        page.update()
    
    def calculate_distribution(e):
        try:
            calculator.total_amount = float(total_amount_field.value or 0)
            
            bets_data = []
            bet_counter = {'本線': 1, '抑え': 1, '狙い': 1}
            
            # データ収集の関数を共通化
            def collect_bets(containers, category_name, target_return):
                for container in containers.controls:
                    if hasattr(container, 'content') and hasattr(container.content, 'controls'):
                        row = container.content
                        if len(row.controls) >= 2:
                            name_field = row.controls[0].controls[0]
                            odds_field = row.controls[1].controls[0]
                            if odds_field.value:
                                name = name_field.value if name_field.value else f"{category_name}{bet_counter[category_name]}"
                                bet_counter[category_name] += 1
                                bets_data.append({
                                    'name': name,
                                    'category': category_name,
                                    'odds': float(odds_field.value),
                                    'target_return': target_return
                                })
            
            collect_bets(main_bets, '本線', float(main_return_field.value or 0))
            collect_bets(suppression_bets, '抑え', float(suppression_return_field.value or 0))
            collect_bets(aim_bets, '狙い', float(aim_return_field.value or 0))
            
            results, warning = calculator.calculate_distribution_strict(bets_data)
            
            if not results and warning:
                # 完全にエラーの場合（賭け対象が設定されていない等）
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"❌ {warning}", color="white"),
                    bgcolor="#ef4444"
                )
                page.snack_bar.open = True
                page.update()
                return
            
            stored_results.clear()
            stored_results.extend(results)
            display_results()
            
            # 警告がある場合は警告を表示、ない場合は成功メッセージ
            if warning:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(warning, color="white"),
                    bgcolor="#f59e0b"
                )
            else:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("✅ 計算が完了しました！", color="white"),
                    bgcolor="#10b981"
                )
            page.snack_bar.open = True
            page.update()
            
        except Exception as ex:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"❌ エラー: {str(ex)}", color="white"),
                bgcolor="#ef4444"
            )
            page.snack_bar.open = True
            page.update()
    
    # ボタンエリア
    buttons_container = ft.Container(
        content=ft.ResponsiveRow([
            ft.Column(
                col={"xs": 12, "sm": 4},
                controls=[create_modern_button("計算実行", calculate_distribution, GRADIENT_PRIMARY, "calculate", True)]
            ),
            ft.Column(
                col={"xs": 12, "sm": 4},
                controls=[create_modern_button("結果コピー", copy_results, GRADIENT_SUCCESS, "content_copy", True)]
            ),
            ft.Column(
                col={"xs": 12, "sm": 4},
                controls=[create_modern_button("リセット", reset_all, GRADIENT_DANGER, "refresh", True)]
            ),
        ]),
        padding=16,
    )
    
    # 結果エリア
    results_card = create_glass_card(
        ft.Column([
            ft.Row([
                ft.Icon("analytics", color="#6366f1", size=20),
                ft.Text("計算結果", size=18, weight=ft.FontWeight.W_600, color="#f8fafc"),
            ], spacing=8),
            ft.Container(height=8),
            summary_text,
            synthetic_odds_text,
            min_bet_info_text,
            ft.Container(height=8),
            results_container,
        ])
    )
    
    # メインレイアウト
    main_content = ft.Column([
        real_admob_banner,  # 上部に本物のAdMob広告
        header,
        settings_card,
        main_section,
        suppression_section,
        aim_section,
        buttons_container,
        results_card,
        ft.Container(height=20),  # 下部余白
    ], scroll=ft.ScrollMode.AUTO, spacing=0)
    
    page.add(main_content)
    
    # 初期データ
    for _ in range(2):
        add_bet_row("main", main_bets)
        add_bet_row("suppression", suppression_bets)
        add_bet_row("aim", aim_bets)
    
    def page_resize(e):
        page.update()
    
    page.on_resize = page_resize


if __name__ == "__main__":
    ft.app(target=main)