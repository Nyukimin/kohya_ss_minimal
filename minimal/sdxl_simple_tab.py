import gradio as gr
import os
from pathlib import Path
from typing import Any
import logging

# ログ設定を最初に定義
log = logging.getLogger(__name__)

# Minimal用プリセット設定を読み込み

from minimal.presets import (
    MINIMAL_DEFAULT_CONFIG,
    SDXL_FACE_LORA_FIXED,
    RESOLUTION_CHOICES,
    BATCH_SIZE_CHOICES,
    SAVE_MODEL_AS_CHOICES,
    SAVE_PRECISION_CHOICES
)

# tomlモジュールをインポート
import toml

def load_user_config() -> dict:
    """
    config.tomlからユーザー設定を動的に読み込む
    
    Design_Requirement_002: Tab.select()時に呼び出され、
    MINIMAL_DEFAULT_CONFIGに上書きして使用される
    
    Returns:
        dict: ユーザー設定（フラット化済み）。読み込み失敗時は空の辞書
    """
    config_path = Path(__file__).parent / "config.toml"
    try:
        if config_path.exists():
            config_data = toml.load(config_path)
            # TOMLの階層構造をフラット化
            user_config = {
                **config_data.get('model', {}),
                **config_data.get('training_data', {}),
                **config_data.get('training_params', {}),
                **config_data.get('output', {})
            }
            log.info(f"Loaded user config from {config_path}")
            return user_config
        else:
            log.info("config.toml not found, using default values")
            return {}
    except Exception as e:
        log.warning(f"Failed to load config.toml: {e}")
        return {}

# フォルダ選択機能をインポート
from kohya_gui.common_gui import get_folder_path, get_file_path

# kohya-ssスタイルのアイコン
folder_symbol = "\U0001f4c2"  # 📂
save_style_symbol = "\U0001f4be"  # 💾
document_symbol = "\U0001F4C4"  # 📄

class SDXLSimpleTab:
    """
    SDXL顔LoRA専用の簡易UIタブ
    既存のLoRAタブと同じ処理を、簡潔なUIで操作するためのインターフェース
    """
    
    def __init__(self, headless: bool = False, config: Any = None, use_shell_flag: bool = False):
        self.headless = headless
        self.config = config
        self.use_shell_flag = use_shell_flag
        self.config_path = Path(__file__).parent / "config.toml"
        
    def create_ui(self):
        """UI作成（Accordion形式、既存スタイルに合わせる）"""
        with gr.Column(variant="compact"):
            gr.Markdown("**SDXL顔LoRA専用の簡易インターフェース** - 必要最小限のパラメータで安全に学習")
            
            # Model Source
            with gr.Accordion("Model Source", open=True):
                with gr.Row():
                    self.pretrained_model_name_or_path = gr.Textbox(
                        label="SDXL Checkpoint path",
                        placeholder="SDXLモデルのパス (.safetensors or .ckpt)",
                        value=MINIMAL_DEFAULT_CONFIG.get('pretrained_model_name_or_path', ''),
                        interactive=True,
                        scale=3
                    )
                    model_file_button = gr.Button(
                        folder_symbol,
                        elem_id="open_folder_small",
                        elem_classes=["tool"],
                        visible=(not self.headless)
                    )
                
                with gr.Row():
                    self.save_model_as = gr.Dropdown(
                        label="Save trained model as",
                        choices=SAVE_MODEL_AS_CHOICES,
                        value=MINIMAL_DEFAULT_CONFIG.get('save_model_as', 'safetensors')
                    )
                    self.save_precision = gr.Dropdown(
                        label="Save precision", 
                        choices=SAVE_PRECISION_CHOICES,
                        value=MINIMAL_DEFAULT_CONFIG.get('save_precision', 'fp16')
                    )
            
            # Training Data
            with gr.Accordion("Training Data", open=True):
                with gr.Row():
                    self.train_data_dir = gr.Textbox(
                        label="Image folder",
                        placeholder="学習画像が含まれるフォルダ",
                        value=MINIMAL_DEFAULT_CONFIG.get('train_data_dir', ''),
                        interactive=True,
                        scale=3
                    )
                    image_folder_button = gr.Button(
                        folder_symbol,
                        elem_id="open_folder_small",
                        elem_classes=["tool"],
                        visible=(not self.headless)
                    )
                
                with gr.Row():
                    self.max_resolution = gr.Dropdown(
                        label="Resolution",
                        choices=RESOLUTION_CHOICES,
                        value=MINIMAL_DEFAULT_CONFIG.get('max_resolution', '512,512'),
                        info="学習解像度（顔LoRAは512x512推奨）"
                    )
                    self.train_batch_size = gr.Dropdown(
                        label="Batch size",
                        choices=BATCH_SIZE_CHOICES,
                        value=MINIMAL_DEFAULT_CONFIG.get('train_batch_size', 1),
                        info="バッチサイズ（1推奨）"
                    )
            
            # Caption Generation
            with gr.Accordion("Caption Generation", open=False):
                gr.Markdown("**固定キャプションを全画像に一括生成** - 学習前の事故を防ぐための補助機能")
                gr.Markdown("*画像フォルダ（Image folder）に指定されたフォルダに自動的にキャプションを生成します*")
                with gr.Row():
                    self.caption_text = gr.Textbox(
                        label="Caption text",
                        placeholder="例: character_name, face, portrait",
                        value=MINIMAL_DEFAULT_CONFIG.get('caption_text', ''),
                        info="全画像に適用する固定キャプションテキスト",
                        lines=2
                    )
                with gr.Row():
                    self.caption_overwrite = gr.Checkbox(
                        label="Overwrite existing captions",
                        value=False,
                        info="既存の.txtファイルがある場合に上書きする（⚠️ 注意: 既存キャプションが失われます）"
                    )
                with gr.Row():
                    self.generate_captions_button = gr.Button(
                        "Generate caption files",
                        variant="secondary",
                        scale=1
                    )
                    self.caption_result = gr.Textbox(
                        label="Caption generation result",
                        value="",
                        interactive=False,
                        lines=3,
                        max_lines=5,
                        scale=2
                    )
            
            # Training Parameters  
            with gr.Accordion("Training Parameters", open=True):
                with gr.Row():
                    self.learning_rate = gr.Textbox(
                        label="Learning rate",
                        value=str(MINIMAL_DEFAULT_CONFIG.get('learning_rate', 0.0001)),
                        info="学習率（U-Net用）"
                    )
                    # Text encoder learning rateのデフォルト値を計算（指数表記を避けるため明示的にフォーマット）
                    text_encoder_lr_default = MINIMAL_DEFAULT_CONFIG.get('text_encoder_lr', MINIMAL_DEFAULT_CONFIG.get('learning_rate', 0.0001) * 0.5)
                    # 指数表記を避けて小数表記で表示（小数点以下5桁まで）
                    text_encoder_lr_str = f"{float(text_encoder_lr_default):.5f}".rstrip('0').rstrip('.')
                    self.text_encoder_lr = gr.Textbox(
                        label="Text encoder learning rate",
                        value=text_encoder_lr_str,
                        info="Text Encoder学習率"
                    )
                
                with gr.Row():
                    self.network_dim = gr.Number(
                        label="LoRA Rank (dim)",
                        value=MINIMAL_DEFAULT_CONFIG.get('network_dim', 16),
                        minimum=1,
                        maximum=128,
                        step=1,
                        info="LoRAの次元数"
                    )
                    self.network_alpha = gr.Number(
                        label="LoRA Alpha",
                        value=MINIMAL_DEFAULT_CONFIG.get('network_alpha', 16),
                        minimum=1,
                        maximum=128,
                        step=1,
                        info="LoRAのアルファ値"
                    )
                
                with gr.Row():
                    self.epoch = gr.Number(
                        label="Epochs",
                        value=MINIMAL_DEFAULT_CONFIG.get('epoch', 6),
                        minimum=1,
                        maximum=100,
                        step=1
                    )
                    self.max_train_steps = gr.Number(
                        label="Max train steps",
                        value=MINIMAL_DEFAULT_CONFIG.get('max_train_steps', 1600),
                        minimum=0,
                        step=100,
                        info="0 = epoch数のみ使用"
                    )
                
                with gr.Row():
                    self.cache_latents = gr.Checkbox(
                        label="Cache latents",
                        value=MINIMAL_DEFAULT_CONFIG.get('cache_latents', True),
                        info="latentsをキャッシュして高速化"
                    )
                    self.cache_latents_to_disk = gr.Checkbox(
                        label="Cache latents to disk",
                        value=MINIMAL_DEFAULT_CONFIG.get('cache_latents_to_disk', False),
                        info="ディスクキャッシュでVRAM節約"
                    )
            
            # Output
            with gr.Accordion("Output", open=True):
                with gr.Row():
                    self.output_name = gr.Textbox(
                        label="Output name",
                        placeholder="character_name_lora",
                        value=MINIMAL_DEFAULT_CONFIG.get('output_name', ''),
                        info="出力するLoRAモデルの名前"
                    )
                
                with gr.Row():
                    self.output_dir = gr.Textbox(
                        label="Output folder",
                        placeholder="出力フォルダ",
                        value=MINIMAL_DEFAULT_CONFIG.get('output_dir', './outputs'),
                        scale=3
                    )
                    output_folder_button = gr.Button(
                        folder_symbol,
                        elem_id="open_folder_small",
                        elem_classes=["tool"],
                        visible=(not self.headless)
                    )
            
            # Training Control
            with gr.Accordion("Training", open=True):
                with gr.Row():
                    self.train_button = gr.Button(
                        "Start training",
                        variant="primary",
                        scale=2
                    )
                    self.save_config_button = gr.Button(
                        "Save Config",
                        variant="secondary",
                        scale=1,
                        interactive=True  # 常に有効
                    )
                    self.stop_button = gr.Button(
                        "Stop training",
                        variant="stop",
                        scale=1
                    )
                
                # hidden の状態変数（ボタン状態管理用）
                import time
                self.run_state = gr.Textbox(value=str(time.time()), visible=False)
                
                # トレーニングサマリー（開始時に表示）
                self.training_summary = gr.Textbox(
                    label="Training Summary",
                    value="",
                    lines=8,
                    max_lines=12,
                    interactive=False,
                    show_copy_button=True
                )
                
                # エポック統計（リアルタイム更新）
                self.epoch_stats = gr.Textbox(
                    label="📈 Epoch Statistics (Loss & Time)",
                    value="Training not started yet...",
                    lines=6,
                    max_lines=10,
                    interactive=False,
                    show_copy_button=True
                )
                
                # リアルタイム進捗ログ
                self.output_log = gr.Textbox(
                    label="Training Progress (Live)",
                    value="Waiting for training to start...",
                    lines=10,
                    max_lines=15,
                    interactive=False,
                    show_copy_button=True,
                    autoscroll=True
                )
                
                # 定期更新用タイマー（1秒間隔）
                self.progress_timer = gr.Timer(value=1, active=False)
            
            # イベント接続
            # フォルダ選択ボタン
            model_file_button.click(
                fn=lambda: get_file_path(
                    default_extension=".safetensors", 
                    extension_name="SDXL Model files"
                ),
                outputs=[self.pretrained_model_name_or_path],
                show_progress=False
            )
            
            image_folder_button.click(
                fn=get_folder_path,
                outputs=[self.train_data_dir],
                show_progress=False
            )
            
            output_folder_button.click(
                fn=get_folder_path,
                outputs=[self.output_dir],
                show_progress=False
            )
            
            # 設定保存ボタン（明示保存フラグ付き）
            explicit_save_flag = gr.State(True)

            self.save_config_button.click(
                fn=self.save_config_and_reset_button,
                inputs=[explicit_save_flag] + self._get_all_inputs(),
                outputs=[self.output_log, self.save_config_button],
                show_progress=False
            )
            
            # 自動保存は廃止（Design_Requirement_002）
            # 代わりに、値変更時にSave Configボタンをハイライト表示
            # Tab.select() による変更はスキップするため、config.toml と比較
            change_components = [
                self.pretrained_model_name_or_path,
                self.train_data_dir,
                self.output_name,
                self.output_dir,
                self.learning_rate,
                self.text_encoder_lr,
                self.network_dim,
                self.network_alpha,
                self.epoch,
                self.max_train_steps,
                self.max_resolution,
                self.train_batch_size,
                self.cache_latents,
                self.cache_latents_to_disk,
                self.save_model_as,
                self.save_precision
            ]
            
            for component in change_components:
                component.change(
                    fn=self._check_config_changed,
                    inputs=self._get_all_inputs(),
                    outputs=[self.save_config_button],
                    show_progress=False
                )
            
            # キャプション生成ボタン
            self.generate_captions_button.click(
                fn=self.generate_captions,
                inputs=[
                    self.caption_text,
                    self.train_data_dir,
                    self.caption_overwrite
                ],
                outputs=[self.caption_result],
                show_progress=True
            )
            
            # 学習開始ボタン
            # start_training() は (train_button, stop_button, run_state, training_summary, timer) を返す
            from kohya_gui.lora_gui import executor
            
            self.train_button.click(
                fn=self.start_training,
                inputs=self._get_all_inputs(),
                outputs=[self.train_button, self.stop_button, self.run_state, self.training_summary, self.progress_timer],
                show_progress=True
            )
            
            # タイマーで定期的に進捗ログを更新
            # タイマーで定期的に進捗ログとエポック統計を更新
            self.progress_timer.tick(
                fn=self._update_progress_log,
                outputs=[self.output_log, self.epoch_stats, self.progress_timer],
                show_progress=False
            )
            
            # run_state が変更されたら、トレーニング終了を待ってボタン状態を復元
            self.run_state.change(
                fn=self._wait_and_stop_timer,
                outputs=[self.train_button, self.stop_button, self.progress_timer, self.output_log, self.epoch_stats],
                show_progress=False
            )
            
            # 学習停止ボタン
            self.stop_button.click(
                fn=self._stop_training,
                outputs=[self.train_button, self.stop_button, self.progress_timer, self.output_log, self.epoch_stats],
                show_progress=False
            )
    
    def _parse_epoch_stats(self, full_output: str) -> str:
        """ログからエポックごとの統計情報を抽出"""
        import re
        
        lines = full_output.split('\n')
        epoch_stats = []
        current_epoch = 0
        epoch_losses = {}
        epoch_times = {}
        start_time = None
        last_epoch_time = None
        
        for line in lines:
            # エポック開始を検出: "epoch 1/6" パターン
            epoch_match = re.search(r'epoch\s+(\d+)/(\d+)', line, re.IGNORECASE)
            if epoch_match:
                new_epoch = int(epoch_match.group(1))
                if new_epoch != current_epoch:
                    if current_epoch > 0 and last_epoch_time:
                        # 前のエポックの時間を記録
                        import time
                        now = time.time()
                        if current_epoch not in epoch_times:
                            epoch_times[current_epoch] = now - last_epoch_time
                    current_epoch = new_epoch
                    import time
                    last_epoch_time = time.time()
            
            # loss値を検出: "loss: 0.0543" または "loss=0.0543" パターン
            loss_match = re.search(r'loss[:\s=]+([0-9.]+)', line, re.IGNORECASE)
            if loss_match and current_epoch > 0:
                loss_val = float(loss_match.group(1))
                if current_epoch not in epoch_losses:
                    epoch_losses[current_epoch] = []
                epoch_losses[current_epoch].append(loss_val)
            
            # ステップ進捗を検出: "step 100/450" または進捗バー
            step_match = re.search(r'(\d+)/(\d+)\s*\[', line)
            if step_match:
                current_step = int(step_match.group(1))
                total_steps = int(step_match.group(2))
        
        # 統計情報を生成
        if not epoch_losses and current_epoch == 0:
            return ""
        
        stats_lines = [
            "",
            "📈 Epoch Statistics:",
            "-" * 40
        ]
        
        for epoch in sorted(epoch_losses.keys()):
            losses = epoch_losses[epoch]
            avg_loss = sum(losses) / len(losses) if losses else 0
            min_loss = min(losses) if losses else 0
            max_loss = max(losses) if losses else 0
            
            time_str = ""
            if epoch in epoch_times:
                mins = int(epoch_times[epoch] // 60)
                secs = int(epoch_times[epoch] % 60)
                time_str = f" | Time: {mins}m {secs}s"
            
            stats_lines.append(
                f"  Epoch {epoch}: Avg Loss={avg_loss:.4f} (Min={min_loss:.4f}, Max={max_loss:.4f}){time_str}"
            )
        
        # 現在のエポック情報
        if current_epoch > 0:
            stats_lines.append(f"\n🔄 Current: Epoch {current_epoch}")
        
        return '\n'.join(stats_lines)
    
    def _update_progress_log(self):
        """タイマーで呼び出され、executorの出力を取得してUIを更新"""
        from kohya_gui.lora_gui import executor
        
        if executor.is_running():
            output = executor.get_output(last_n_lines=50)  # より多くのログを表示
            full_output = executor.get_output(last_n_lines=500)  # 統計用に全ログ取得
            epoch_stats = self._parse_epoch_stats(full_output)
            
            if output:
                return (
                    gr.Textbox(value=output),
                    gr.Textbox(value=epoch_stats) if epoch_stats else gr.Textbox(),
                    gr.Timer(active=True)
                )
            else:
                return (
                    gr.Textbox(value="Training in progress..."),
                    gr.Textbox(),
                    gr.Timer(active=True)
                )
        else:
            # トレーニング終了
            output = executor.get_output(last_n_lines=30)
            full_output = executor.get_output(last_n_lines=500)
            epoch_stats = self._parse_epoch_stats(full_output)
            
            # 終了コードを確認
            exit_code = executor.process.poll() if executor.process else None
            if exit_code is not None and exit_code != 0:
                final_msg = output + f"\n\n❌ Training failed! (Exit code: {exit_code})"
                status_msg = "❌ Error" if not epoch_stats else epoch_stats + f"\n\n❌ Error (code: {exit_code})"
            else:
                final_msg = output + "\n\n✅ Training completed!" if output else "✅ Training completed!"
                status_msg = epoch_stats + "\n\n✅ Complete!" if epoch_stats else ""
            
            return (
                gr.Textbox(value=final_msg),
                gr.Textbox(value=status_msg) if status_msg else gr.Textbox(),
                gr.Timer(active=False)
            )
    
    def _wait_and_stop_timer(self):
        """トレーニング終了を待ってタイマーを停止し、ボタン状態を復元"""
        from kohya_gui.lora_gui import executor
        
        while executor.is_running():
            import time
            time.sleep(1)
        
        # 最終出力を取得
        output = executor.get_output(last_n_lines=30)
        full_output = executor.get_output(last_n_lines=500)
        epoch_stats = self._parse_epoch_stats(full_output)
        
        # 終了コードを確認
        exit_code = executor.process.poll() if executor.process else None
        if exit_code is not None and exit_code != 0:
            final_msg = output + f"\n\n❌ Training failed! (Exit code: {exit_code})"
            status_msg = "❌ Error" if not epoch_stats else epoch_stats + f"\n\n❌ Error (code: {exit_code})"
        else:
            final_msg = output + "\n\n✅ Training completed!" if output else "✅ Training completed!"
            status_msg = epoch_stats + "\n\n✅ Complete!" if epoch_stats else ""
        
        return (
            gr.Button(visible=True),   # train_button
            gr.Button(visible=False),  # stop_button
            gr.Timer(active=False),    # timer
            gr.Textbox(value=final_msg),  # output_log
            gr.Textbox(value=status_msg) if status_msg else gr.Textbox()  # epoch_stats
        )
    
    def _stop_training(self):
        """トレーニングを停止"""
        from kohya_gui.lora_gui import executor
        
        # 停止前に統計を取得
        full_output = executor.get_output(last_n_lines=500)
        epoch_stats = self._parse_epoch_stats(full_output)
        
        executor.kill_command()
        
        output = executor.get_output(last_n_lines=30)
        final_msg = output + "\n\n⚠️ Training stopped by user." if output else "⚠️ Training stopped by user."
        
        return (
            gr.Button(visible=True),   # train_button
            gr.Button(visible=False),  # stop_button
            gr.Timer(active=False),    # timer
            gr.Textbox(value=final_msg),  # output_log
            gr.Textbox(value=epoch_stats + "\n\n⚠️ Stopped") if epoch_stats else gr.Textbox()  # epoch_stats
        )
    
    def _get_all_inputs(self):
        """すべての入力要素をリストで返す（train_model関数の引数順）"""
        return [
            # UI inputs
            self.pretrained_model_name_or_path,
            self.train_data_dir,
            self.output_name,
            self.output_dir,
            self.learning_rate,
            self.text_encoder_lr,
            self.network_dim,
            self.network_alpha,
            self.epoch,
            self.max_train_steps,
            self.max_resolution,
            self.train_batch_size,
            self.cache_latents,
            self.cache_latents_to_disk,
            self.save_model_as,
            self.save_precision
        ]
    
    def _check_config_changed(self, *args):
        """UIの値がconfig.tomlと異なるかチェックし、ボタンをハイライト
        
        Tab.select() による変更をスキップするため、config.toml と比較。
        値が異なる場合のみハイライト表示する。
        """
        try:
            # config.toml を読み込み
            config = MINIMAL_DEFAULT_CONFIG.copy()
            user_config = load_user_config()
            config.update(user_config)
            
            
            # UI値を取得
            ui_values = {
                'pretrained_model_name_or_path': args[0] if args[0] else '',
                'train_data_dir': args[1] if args[1] else '',
                'output_name': args[2] if args[2] is not None else '',
                'output_dir': args[3] if args[3] is not None else './outputs',
                'learning_rate': str(args[4]) if args[4] else '0.0001',
                'text_encoder_lr': str(args[5]) if args[5] else '0.00005',
                'network_dim': int(args[6]) if args[6] else 16,
                'network_alpha': int(args[7]) if args[7] else 16,
                'epoch': int(args[8]) if args[8] else 6,
                'max_train_steps': int(args[9]) if args[9] else 1600,
                'max_resolution': str(args[10]) if args[10] else '512,512',
                'train_batch_size': int(args[11]) if args[11] else 1,
                'cache_latents': bool(args[12]) if args[12] is not None else True,
                'cache_latents_to_disk': bool(args[13]) if args[13] is not None else False,
                'save_model_as': args[14] if args[14] else 'safetensors',
                'save_precision': args[15] if args[15] else 'fp16'
            }
            
            # 比較（一部の値は型を揃える）
            is_changed = False
            for key, ui_value in ui_values.items():
                config_value = config.get(key, '')
                
                # 型を揃えて比較
                if key in ['learning_rate', 'text_encoder_lr']:
                    # 浮動小数点の比較
                    try:
                        ui_float = float(ui_value)
                        config_float = float(config_value) if config_value else 0.0
                        if abs(ui_float - config_float) > 1e-10:
                            is_changed = True
                            break
                    except (ValueError, TypeError):
                        is_changed = True
                        break
                elif isinstance(ui_value, bool):
                    config_bool = bool(config_value) if config_value is not None else False
                    if ui_value != config_bool:
                        is_changed = True
                        break
                elif isinstance(ui_value, int):
                    try:
                        config_int = int(config_value) if config_value else 0
                        if ui_value != config_int:
                            is_changed = True
                            break
                    except (ValueError, TypeError):
                        is_changed = True
                        break
                else:
                    if str(ui_value) != str(config_value):
                        is_changed = True
                        break
            
            if is_changed:
                return gr.update(value="💾 Save Config *", variant="primary")
            else:
                return gr.update(value="Save Config", variant="secondary")
        except Exception as e:
            log.warning(f"Config change check failed: {e}")
            # エラー時はハイライトしない
            return gr.update()
    
    def get_ui_outputs(self):
        """Tab.select()のoutputsとして使用するUIコンポーネントのリストを返す"""
        return [
            self.pretrained_model_name_or_path,
            self.train_data_dir,
            self.output_name,
            self.output_dir,
            self.learning_rate,
            self.text_encoder_lr,
            self.network_dim,
            self.network_alpha,
            self.epoch,
            self.max_train_steps,
            self.max_resolution,
            self.train_batch_size,
            self.cache_latents,
            self.cache_latents_to_disk,
            self.save_model_as,
            self.save_precision,
            self.save_config_button  # タブ選択時にボタンをリセット
        ]
    
    def load_and_update_ui(self):
        """
        タブ選択時にDEFAULT→CONFIGの順で読み込み、UIを更新
        
        設計原則:
        - 常に同じシーケンス（DEFAULT→CONFIG上書き）を通る
        - CONFIGの有無に関わらず同じコードパスを通ることでバグを減らす
        
        Returns:
            tuple: gr.update()のタプル（get_ui_outputs()の順序と一致）
        """
        # 1. DEFAULTで初期化
        config = MINIMAL_DEFAULT_CONFIG.copy()
        
        # 2. CONFIGで上書き
        user_config = load_user_config()
        config.update(user_config)
        
        log.info(f"UI updated with config: {len(user_config)} user settings applied")
        
        # 3. text_encoder_lr を小数表記でフォーマット
        text_encoder_lr_value = config.get('text_encoder_lr', config.get('learning_rate', 0.0001) * 0.5)
        text_encoder_lr_str = f"{float(text_encoder_lr_value):.5f}".rstrip('0').rstrip('.')
        
        # 4. gr.update()でUIを更新（get_ui_outputs()の順序と一致）
        return (
            gr.update(value=config.get('pretrained_model_name_or_path', '')),
            gr.update(value=config.get('train_data_dir', '')),
            gr.update(value=config.get('output_name', '')),
            gr.update(value=config.get('output_dir', './outputs')),
            gr.update(value=str(config.get('learning_rate', 0.0001))),
            gr.update(value=text_encoder_lr_str),
            gr.update(value=config.get('network_dim', 16)),
            gr.update(value=config.get('network_alpha', 16)),
            gr.update(value=config.get('epoch', 6)),
            gr.update(value=config.get('max_train_steps', 1600)),
            gr.update(value=config.get('max_resolution', '512,512')),
            gr.update(value=config.get('train_batch_size', 1)),
            gr.update(value=config.get('cache_latents', True)),
            gr.update(value=config.get('cache_latents_to_disk', False)),
            gr.update(value=config.get('save_model_as', 'safetensors')),
            gr.update(value=config.get('save_precision', 'fp16')),
            gr.update(value="Save Config", variant="secondary")  # ボタンをリセット
        )
    
    def generate_captions(
        self,
        caption_text: str,
        train_data_dir: str,
        overwrite: bool
    ) -> str:
        """
        固定キャプションを全画像に一括生成
        
        Specification_001.md ⑥ Caption一括生成（重要）の要件を満たす
        
        Args:
            caption_text: 固定キャプションテキスト
            train_data_dir: 学習画像フォルダパス（Image folderで指定されたフォルダを自動使用）
            overwrite: 既存キャプションを上書きするか
            
        Returns:
            str: 生成結果メッセージ
        """
        try:
            # 入力検証
            if not caption_text or not caption_text.strip():
                return "エラー: キャプションテキストを入力してください"
            
            if not train_data_dir or not train_data_dir.strip():
                return "エラー: 画像フォルダ（Image folder）を指定してください"
            
            # パスの正規化
            train_data_dir_path = os.path.normpath(train_data_dir.strip())
            
            if not os.path.exists(train_data_dir_path):
                return f"エラー: 指定されたフォルダが存在しません: {train_data_dir_path}"
            
            if not os.path.isdir(train_data_dir_path):
                return f"エラー: 指定されたパスはフォルダではありません: {train_data_dir_path}"
            
            # kohya_ssの仕様: train_data_dirの下にあるサブフォルダ（1個）を自動検出
            subfolders = [
                f
                for f in os.listdir(train_data_dir_path)
                if os.path.isdir(os.path.join(train_data_dir_path, f))
            ]
            
            if len(subfolders) == 0:
                return f"エラー: {train_data_dir_path} の下にサブフォルダが見つかりません。kohya_ssの仕様に従い、サブフォルダ（例: 5_SATOMI）を作成してください。"
            
            if len(subfolders) > 1:
                return f"エラー: {train_data_dir_path} の下に複数のサブフォルダが見つかりました: {', '.join(subfolders)}。今回は1つのサブフォルダのみをサポートしています。"
            
            # 実際に使用するフォルダ（サブフォルダ）
            images_dir = os.path.join(train_data_dir_path, subfolders[0])
            log.info(f"Caption生成対象フォルダ: {images_dir}")
            
            # 既存キャプションファイルの確認（上書き確認）
            if not overwrite:
                import glob
                caption_files = glob.glob(os.path.join(images_dir, "*.txt"))
                if caption_files:
                    file_count = len(caption_files)
                    return f"警告: 既存のキャプションファイルが{file_count}個見つかりました。上書きする場合は「Overwrite existing captions」をチェックしてください。"
            
            # 既存のcaption_images関数をインポート
            from kohya_gui.basic_caption_gui import caption_images
            
            # caption_images関数を呼び出し
            caption_images(
                caption_text=caption_text.strip(),
                images_dir=images_dir,
                overwrite=overwrite,
                caption_ext=".txt",
                prefix="",
                postfix="",
                find_text="",
                replace_text=""
            )
            
            # 生成されたキャプションファイル数を確認
            # 画像ファイル（Jpeg系）のみをカウント
            image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}
            image_extensions_upper = {ext.upper() for ext in image_extensions}
            
            image_count = 0
            caption_count = 0
            
            # フォルダ内のファイルを列挙してカウント
            for filename in os.listdir(images_dir):
                file_path = os.path.join(images_dir, filename)
                if os.path.isfile(file_path):
                    # 拡張子を取得（小文字に変換）
                    _, ext = os.path.splitext(filename)
                    ext_lower = ext.lower()
                    
                    # 画像ファイル（Jpeg系）をカウント
                    if ext_lower in image_extensions or ext in image_extensions_upper:
                        image_count += 1
                    # キャプションファイル（.txt）をカウント
                    elif ext_lower == '.txt':
                        caption_count += 1
            
            result_msg = f"✓ キャプションファイル生成完了\n"
            result_msg += f"  画像ファイル（Jpeg系）: {image_count}個\n"
            result_msg += f"  キャプションファイル（.txt）: {caption_count}個"
            
            log.info(result_msg)
            return result_msg
            
        except Exception as e:
            error_msg = f"エラー: キャプション生成に失敗しました - {str(e)}"
            log.error(error_msg)
            return error_msg
    
    def _generate_minimal_params(
        self,
        pretrained_model_name_or_path,
        train_data_dir,
        output_name,
        output_dir,
        learning_rate,
        text_encoder_lr,
        network_dim,
        network_alpha,
        epoch,
        max_train_steps,
        max_resolution,
        train_batch_size,
        cache_latents,
        cache_latents_to_disk,
        save_model_as,
        save_precision
    ) -> dict:
        """
        MinimalタブのUI入力値から16個のパラメータを辞書形式で生成
        
        Returns:
            dict: Minimalタブのパラメータ辞書（16個）
        """
        return {
            'pretrained_model_name_or_path': pretrained_model_name_or_path,
            'train_data_dir': train_data_dir,
            'output_name': output_name,
            'output_dir': output_dir,
            'learning_rate': float(learning_rate) if learning_rate else 0.0001,
            'text_encoder_lr': float(text_encoder_lr) if text_encoder_lr else 0.00005,
            'network_dim': int(network_dim) if network_dim else 16,
            'network_alpha': int(network_alpha) if network_alpha else 16,
            'epoch': int(epoch) if epoch else 6,
            'max_train_steps': int(max_train_steps) if max_train_steps else 0,
            'max_resolution': max_resolution if max_resolution else '512,512',
            'train_batch_size': int(train_batch_size) if train_batch_size else 1,
            'cache_latents': bool(cache_latents) if cache_latents is not None else True,
            'cache_latents_to_disk': bool(cache_latents_to_disk) if cache_latents_to_disk is not None else False,
            'save_model_as': save_model_as if save_model_as else 'safetensors',
            'save_precision': save_precision if save_precision else 'fp16'
        }
    
    def _get_training_defaults(self) -> dict:
        """
        TrainingタブのUIコンポーネントの初期値（デフォルト値）を取得
        
        注意: デフォルト値を「生成」するのではなく、
        TrainingタブのUIコンポーネントの初期値と同じ値を使用する
        
        Returns:
            dict: Trainingタブのデフォルト値辞書（229個のパラメータ）
        """
        # TrainingタブのUIコンポーネントの初期値（lora_gui.pyから取得）
        # ImplementationSpecification_Design_Requirement_001_VERIFIED.md に基づく
        
        defaults = {
            # source model section（train_model関数の引数順序に従う）
            'v2': False,
            'v_parameterization': False,
            'sdxl': True,  # SDXL固定（MinimalタブはSDXL専用）
            'flux1_checkbox': False,
            'dataset_config': '',
            'model_list': '',
            'training_comment': '',
            
            # folders section
            'logging_dir': '',
            'reg_data_dir': '',
            
            # basic training section
            'lr_scheduler': 'cosine',
            'lr_warmup': 10,
            'lr_warmup_steps': 0,
            'save_every_n_epochs': 0,
            'seed': '',
            'caption_extension': '.txt',
            'enable_bucket': False,
            'stop_text_encoder_training': 0,
            'min_bucket_reso': 256,
            'max_bucket_reso': 1024,
            'max_train_epochs': 0,
            'lr_scheduler_num_cycles': 1,
            'lr_scheduler_power': 1.0,
            'optimizer': 'adamw8bit',
            'optimizer_args': '',
            'lr_scheduler_args': '',
            'lr_scheduler_type': '',
            'max_grad_norm': 1.0,
            
            # accelerate launch section
            'mixed_precision': 'fp16',
            'num_cpu_threads_per_process': 1,
            'num_processes': 1,
            'num_machines': 1,
            'multi_gpu': False,
            'gpu_ids': '',
            'main_process_port': 29500,
            'dynamo_backend': '',
            'dynamo_mode': '',
            'dynamo_use_fullgraph': False,
            'dynamo_use_dynamic': False,
            'extra_accelerate_launch_args': '',
            
            # advanced training section
            'gradient_checkpointing': False,
            'fp8_base': False,
            'fp8_base_unet': False,
            'full_fp16': False,
            'highvram': False,
            'lowvram': False,
            'xformers': False,
            'shuffle_caption': False,
            'save_state': False,
            'save_state_on_train_end': False,
            'resume': '',
            'prior_loss_weight': 1.0,
            'color_aug': False,
            'flip_aug': False,
            'masked_loss': False,
            'clip_skip': 1,
            'gradient_accumulation_steps': 1,
            'mem_eff_attn': False,
            'max_token_length': 75,
            'max_data_loader_n_workers': 0,
            'keep_tokens': 0,
            'persistent_data_loader_workers': False,
            'bucket_no_upscale': False,
            'random_crop': False,
            'bucket_reso_steps': 64,
            'v_pred_like_loss': 0,
            'caption_dropout_every_n_epochs': 0,
            'caption_dropout_rate': 0,
            'noise_offset_type': 'original',
            'noise_offset': 0,
            'noise_offset_random_strength': False,
            'adaptive_noise_scale': 0,
            'multires_noise_iterations': 0,
            'multires_noise_discount': 0,
            'ip_noise_gamma': 0,
            'ip_noise_gamma_random_strength': 0,
            'additional_parameters': '',
            'loss_type': 'l2',
            'huber_schedule': 'snr',
            'huber_c': 0.1,
            'huber_scale': 0.1,
            'vae_batch_size': 0,
            'min_snr_gamma': 0,
            'save_every_n_steps': 0,
            'save_last_n_steps': 0,
            'save_last_n_steps_state': 0,
            'save_last_n_epochs': 0,
            'save_last_n_epochs_state': 0,
            'skip_cache_check': False,
            'log_with': '',
            'wandb_api_key': '',
            'wandb_run_name': '',
            'log_tracker_name': '',
            'log_tracker_config': '',
            'log_config': '',
            'scale_v_pred_loss_like_noise_pred': False,
            'full_bf16': False,
            'min_timestep': 0,
            'max_timestep': 1000,
            'vae': '',
            'weighted_captions': False,
            'debiased_estimation_loss': False,
            
            # sdxl parameters section
            'sdxl_cache_text_encoder_outputs': False,
            'sdxl_no_half_vae': False,
            
            # LoRA network section
            'text_encoder_lr': 0.00005,  # Minimalタブで上書きされる
            't5xxl_lr': 0,
            'unet_lr': 0.0001,
            'network_weights': '',
            'dim_from_weights': False,
            'network_dim': 16,  # Minimalタブで上書きされる
            'network_alpha': 16,  # Minimalタブで上書きされる
            'LoRA_type': 'Standard',
            'factor': -1,
            'bypass_mode': False,
            'dora_wd': False,
            'use_cp': False,
            'use_tucker': False,
            'use_scalar': False,
            'rank_dropout_scale': False,
            'constrain': 0.0,
            'rescaled': False,
            'train_norm': False,
            'decompose_both': False,
            'train_on_input': True,
            'conv_dim': 32,
            'conv_alpha': 1,
            'sample_every_n_steps': 0,
            'sample_every_n_epochs': 0,
            'sample_sampler': 'euler_a',
            'sample_prompts': '',
            'down_lr_weight': '',
            'mid_lr_weight': '',
            'up_lr_weight': '',
            'block_lr_zero_threshold': 0,
            'block_dims': '',
            'block_alphas': '',
            'conv_block_dims': '',
            'conv_block_alphas': '',
            'unit': 1,
            'scale_weight_norms': 1.0,
            'network_dropout': 0,
            'rank_dropout': 0,
            'module_dropout': 0,
            'LyCORIS_preset': 'full',
            'loraplus_lr_ratio': 0,
            'loraplus_text_encoder_lr_ratio': 0,
            'loraplus_unet_lr_ratio': 0,
            'train_lora_ggpo': False,
            'ggpo_sigma': 0.5,
            'ggpo_beta': 0.5,
            
            # huggingface section
            'huggingface_repo_id': '',
            'huggingface_token': '',
            'huggingface_repo_type': 'model',
            'huggingface_repo_visibility': 'private',
            'huggingface_path_in_repo': '',
            'save_state_to_huggingface': False,
            'resume_from_huggingface': False,
            'async_upload': False,
            
            # metadata section
            'metadata_author': '',
            'metadata_description': '',
            'metadata_license': '',
            'metadata_tags': '',
            'metadata_title': '',
            
            # Flux1 parameters
            'flux1_cache_text_encoder_outputs': False,
            'flux1_cache_text_encoder_outputs_to_disk': False,
            'ae': '',
            'clip_l': '',
            't5xxl': '',
            'discrete_flow_shift': 3.0,
            'model_prediction_type': 'epsilon',
            'timestep_sampling': 'leading',
            'split_mode': 'alternating',
            'train_blocks': 'all',
            't5xxl_max_token_length': 512,
            'enable_all_linear': False,
            'guidance_scale': 3.5,
            'mem_eff_save': False,
            'apply_t5_attn_mask': False,
            'split_qkv': False,
            'train_t5xxl': False,
            'cpu_offload_checkpointing': False,
            'blocks_to_swap': 4,
            'single_blocks_to_swap': 4,
            'double_blocks_to_swap': 4,
            'img_attn_dim': 0,
            'img_mlp_dim': 0,
            'img_mod_dim': 0,
            'single_dim': 0,
            'txt_attn_dim': 0,
            'txt_mlp_dim': 0,
            'txt_mod_dim': 0,
            'single_mod_dim': 0,
            'in_dims': '',
            'train_double_block_indices': '',
            'train_single_block_indices': '',
            
            # SD3 parameters
            'sd3_cache_text_encoder_outputs': False,
            'sd3_cache_text_encoder_outputs_to_disk': False,
            'sd3_fused_backward_pass': False,
            'clip_g': '',
            'clip_g_dropout_rate': 0,
            'sd3_clip_l': '',
            'sd3_clip_l_dropout_rate': 0,
            'sd3_disable_mmap_load_safetensors': False,
            'sd3_enable_scaled_pos_embed': False,
            'logit_mean': 0,
            'logit_std': 0,
            'mode_scale': 0,
            'pos_emb_random_crop_rate': 0,
            'save_clip': False,
            'save_t5xxl': False,
            'sd3_t5_dropout_rate': 0,
            'sd3_t5xxl': '',
            't5xxl_device': '',
            't5xxl_dtype': '',
            'sd3_text_encoder_batch_size': 1,
            'weighting_scheme': 'sigma_sqrt',
            'sd3_checkbox': False,
        }
        
        # SDXL顔LoRA用の最適化済みデフォルト値を適用
        defaults.update(MINIMAL_DEFAULT_CONFIG)
        defaults.update(SDXL_FACE_LORA_FIXED)
        
        return defaults
    
    def _merge_params(self, training_defaults: dict, minimal_params: dict) -> dict:
        """
        Trainingタブのデフォルト値に、Minimalタブで設定した値を上書き
        
        Args:
            training_defaults: Trainingタブのデフォルト値辞書（229個）
            minimal_params: Minimalタブのパラメータ辞書（16個）
            
        Returns:
            dict: マージ後のパラメータ辞書（229個）
        """
        # Trainingタブのデフォルト値に、Minimalタブの値を上書き
        final_params = {**training_defaults, **minimal_params}
        return final_params
    
    def _build_settings_list(self, params: dict) -> list:
        """
        settings_list を構築（Trainingタブと同じ順序）
        
        Args:
            params: マージ後のパラメータ辞書（229個）
            
        Returns:
            list: train_model関数に渡すsettings_list（229個の実際の値）
        """
        from minimal.utils import build_settings_list_from_params
        return build_settings_list_from_params(params)
    
    def start_training(
        self,
        pretrained_model_name_or_path,
        train_data_dir, 
        output_name,
        output_dir,
        learning_rate,
        text_encoder_lr,
        network_dim,
        network_alpha,
        epoch,
        max_train_steps,
        max_resolution,
        train_batch_size,
        cache_latents,
        cache_latents_to_disk,
        save_model_as,
        save_precision
    ):
        """
        学習開始 - Design_Requirement_001.md に基づく実装（5ステップフロー）
        
        1. Minimalパラメータ生成（16個）
        2. Trainingタブのデフォルト値を取得（UIコンポーネントの初期値、生成しない）
        3. Minimalパラメータマージ
        4. settings_list を構築（train_model関数の引数順序と完全に一致）
        5. train_model() 関数を既存と同じ方法で呼び出す
        """
        import time
        
        # エラー時の戻り値ヘルパー（train_button表示、stop_button非表示、timer停止）
        def error_return(msg):
            return (
                gr.Button(visible=True),   # train_button を表示
                gr.Button(visible=False),  # stop_button を非表示
                gr.Textbox(),              # run_state（変更なし）
                gr.Textbox(value=msg),     # training_summary: エラーメッセージ
                gr.Timer(active=False)     # timer: 停止
            )
        
        try:
            # 入力検証
            if not pretrained_model_name_or_path:
                return error_return("エラー: チェックポイントパスが必要です")
            if not train_data_dir or not os.path.exists(train_data_dir):
                return error_return("エラー: 有効な画像フォルダが必要です")
            if not output_name:
                return error_return("エラー: 出力名が必要です")
            if not output_dir:
                return error_return("エラー: 出力フォルダが必要です")
            
            # ステップ1: Minimalパラメータ生成（16個）
            minimal_params = self._generate_minimal_params(
                pretrained_model_name_or_path,
                train_data_dir,
                output_name,
                output_dir,
                learning_rate,
                text_encoder_lr,
                network_dim,
                network_alpha,
                epoch,
                max_train_steps,
                max_resolution,
                train_batch_size,
                cache_latents,
                cache_latents_to_disk,
                save_model_as,
                save_precision
            )
            
            # ステップ2: Trainingタブのデフォルト値を取得（UIコンポーネントの初期値、生成しない）
            training_defaults = self._get_training_defaults()
            
            # ステップ3: Minimalパラメータマージ
            final_params = self._merge_params(training_defaults, minimal_params)
            
            # 注: down_lr_weight/up_lr_weight はU-Netブロック単位の学習率重み設定用。
            #     SDXLでは9個のブロックに対応したカンマ区切りリストが必要。
            #     Text Encoder学習率は text_encoder_lr パラメータで別途設定済み。
            #     ここでは追加のブロック単位制御は行わない。
            
            # ステップ4: settings_list を構築（train_model関数の引数順序と完全に一致）
            settings_list = self._build_settings_list(final_params)
            
            # パラメータ数の検証（headlessとprint_onlyを除く229個）
            import inspect
            from kohya_gui.lora_gui import train_model as tm_check
            expected_count = len(inspect.signature(tm_check).parameters) - 2  # headless, print_only を除く
            actual_count = len(settings_list)
            log.info(f"Parameter count verification: expected={expected_count}, actual={actual_count}")
            if actual_count != expected_count:
                log.warning(f"Parameter count mismatch! Expected {expected_count}, got {actual_count}")
            
            # トレーニング情報のサマリーを生成
            training_summary = self._generate_training_summary(
                pretrained_model_name_or_path,
                train_data_dir,
                output_name,
                output_dir,
                learning_rate,
                text_encoder_lr,
                network_dim,
                network_alpha,
                epoch,
                max_train_steps,
                max_resolution,
                train_batch_size,
                cache_latents,
                cache_latents_to_disk
            )
            
            # ステップ5: train_model() 関数を既存と同じ方法で呼び出す
            # headless, print_only は位置引数として渡す（キーワード引数だと*settings_listと競合）
            from kohya_gui.lora_gui import train_model
            result = train_model(
                self.headless,  # 位置引数: headless
                False,          # 位置引数: print_only
                *settings_list  # 残りの229個の位置引数
            )
            
            # train_model は (train_button, stop_button, run_state_value) のタプルを返す
            if result:
                train_btn, stop_btn, run_state_textbox = result
                return (
                    train_btn,
                    stop_btn,
                    run_state_textbox,  # run_state: 状態管理用
                    gr.Textbox(value=training_summary),  # training_summary: サマリー表示
                    gr.Timer(active=True)  # timer: 進捗更新を開始
                )
            else:
                return error_return("学習が完了しました")
            
        except Exception as e:
            error_msg = f"エラー: {str(e)}"
            log.error(error_msg, exc_info=True)
            return error_return(error_msg)
    
    def _generate_training_summary(
        self,
        pretrained_model_name_or_path,
        train_data_dir,
        output_name,
        output_dir,
        learning_rate,
        text_encoder_lr,
        network_dim,
        network_alpha,
        epoch,
        max_train_steps,
        max_resolution,
        train_batch_size,
        cache_latents,
        cache_latents_to_disk
    ) -> str:
        """トレーニング情報のサマリーを生成"""
        import os
        from datetime import datetime
        
        # 画像数をカウント
        image_count = 0
        repeats = 0
        subfolder_name = ""
        if train_data_dir and os.path.exists(train_data_dir):
            for item in os.listdir(train_data_dir):
                item_path = os.path.join(train_data_dir, item)
                if os.path.isdir(item_path):
                    subfolder_name = item
                    # repeats_class 形式のフォルダ名からrepeats数を取得
                    parts = item.split('_')
                    if parts and parts[0].isdigit():
                        repeats = int(parts[0])
                    # 画像ファイルをカウント
                    for file in os.listdir(item_path):
                        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp')):
                            image_count += 1
                    break
        
        total_steps = image_count * repeats * int(epoch) if repeats > 0 else 0
        effective_steps = min(total_steps, int(max_train_steps)) if int(max_train_steps) > 0 else total_steps
        
        lines = [
            "=" * 50,
            f"  🚀 Training Started - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 50,
            "",
            "📁 Model & Data:",
            f"  • Checkpoint: {os.path.basename(pretrained_model_name_or_path)}",
            f"  • Training folder: {subfolder_name}",
            f"  • Images: {image_count} × {repeats} repeats = {image_count * repeats} steps/epoch",
            f"  • Output: {output_name}",
            "",
            "⚙️ Training Parameters:",
            f"  • Resolution: {max_resolution}",
            f"  • Batch size: {train_batch_size}",
            f"  • Epochs: {epoch}",
            f"  • Max train steps: {max_train_steps if int(max_train_steps) > 0 else 'Unlimited'}",
            f"  • Effective steps: ~{effective_steps}",
            "",
            "📊 Learning Rates:",
            f"  • U-Net LR: {learning_rate}",
            f"  • Text Encoder LR: {text_encoder_lr}",
            "",
            "🔧 LoRA Settings:",
            f"  • Network dim (rank): {network_dim}",
            f"  • Network alpha: {network_alpha}",
            "",
            "💾 Cache Settings:",
            f"  • Cache latents: {cache_latents}",
            f"  • Cache to disk: {cache_latents_to_disk}",
            "",
            "=" * 50,
            "  Training in progress... Check console for details.",
            "=" * 50,
        ]
        
        return "\n".join(lines)
    
    def save_config(self, explicit_save: bool, *args):
        """設定値をconfig.tomlに保存

        Args:
            explicit_save: True の場合は明示保存としてメッセージを返す
        """
        try:
            import toml
            
            is_explicit_save = bool(explicit_save)
            
            # 現在の設定値を取得
            # _get_all_inputs()の順序に合わせて引数を取得:
            # explicit_save は別の引数として渡される（*argsには含まれない）
            # args[0]: pretrained_model_name_or_path (_get_all_inputs()[0])
            # args[1]: train_data_dir (_get_all_inputs()[1])
            # args[2]: output_name (_get_all_inputs()[2])
            # args[3]: output_dir (_get_all_inputs()[3])
            # args[4]: learning_rate (_get_all_inputs()[4])
            # args[5]: text_encoder_lr (_get_all_inputs()[5])
            # args[6]: network_dim (_get_all_inputs()[6])
            # args[7]: network_alpha (_get_all_inputs()[7])
            # args[8]: epoch (_get_all_inputs()[8])
            # args[9]: max_train_steps (_get_all_inputs()[9])
            # args[10]: max_resolution (_get_all_inputs()[10])
            # args[11]: train_batch_size (_get_all_inputs()[11])
            # args[12]: cache_latents (_get_all_inputs()[12])
            # args[13]: cache_latents_to_disk (_get_all_inputs()[13])
            # args[14]: save_model_as (_get_all_inputs()[14])
            # args[15]: save_precision (_get_all_inputs()[15])
            
            config_data = {
                'model': {
                    'pretrained_model_name_or_path': args[0] if len(args) > 0 and args[0] else '',
                    'save_model_as': args[14] if len(args) > 14 and args[14] else 'safetensors',
                    'save_precision': args[15] if len(args) > 15 and args[15] else 'fp16'
                },
                'training_data': {
                    'train_data_dir': args[1] if len(args) > 1 and args[1] else '',
                    'max_resolution': str(args[10]) if len(args) > 10 and args[10] else "512,512",
                    'train_batch_size': int(args[11]) if len(args) > 11 and args[11] else 1
                },
                'training_params': {
                    'learning_rate': float(args[4]) if len(args) > 4 and args[4] else 0.0001,
                    'text_encoder_lr': float(args[5]) if len(args) > 5 and args[5] else 0.00005,
                    'network_dim': int(args[6]) if len(args) > 6 and args[6] else 16,
                    'network_alpha': int(args[7]) if len(args) > 7 and args[7] else 16,
                    'epoch': int(args[8]) if len(args) > 8 and args[8] else 6,
                    'max_train_steps': int(args[9]) if len(args) > 9 and args[9] else 1600,
                    'cache_latents': bool(args[12]) if len(args) > 12 and args[12] is not None else True,
                    'cache_latents_to_disk': bool(args[13]) if len(args) > 13 and args[13] is not None else False
                },
                'output': {
                    'output_name': args[2] if len(args) > 2 and args[2] is not None else '',
                    'output_dir': args[3] if len(args) > 3 and args[3] is not None else './outputs'
                }
            }
            
            # TOMLファイルに書き込み
            with open(self.config_path, 'w', encoding='utf-8') as f:
                f.write("# SDXL Face LoRA Minimal Configuration\n")
                f.write("# SDXL顔LoRA学習用のユーザー設定\n")
                f.write("# このファイルを編集して、UIの初期値をカスタマイズできます\n\n")
                toml.dump(config_data, f)
            
            log.info(f"Settings saved to {self.config_path}")
            
            # 明示的な保存かオートセーブかでメッセージを変える
            if is_explicit_save:
                return "設定をconfig.tomlに保存しました"
            else:
                return ""  # オートセーブの場合はメッセージを表示しない
            
        except Exception as e:
            error_msg = f"設定の保存に失敗しました: {str(e)}"
            log.error(error_msg)
            return error_msg
    
    def save_config_and_reset_button(self, explicit_save: bool, *args):
        """設定を保存し、Save Configボタンを元に戻す
        
        Returns:
            tuple: (output_log メッセージ, ボタン更新)
        """
        result = self.save_config(explicit_save, *args)
        # 保存成功時はボタンを元に戻す
        if "失敗" not in result and "エラー" not in result:
            return result, gr.update(value="Save Config", variant="secondary")
        else:
            # エラー時はハイライトを維持
            return result, gr.update()
    
    def _convert_ui_to_train_args(
        self, 
        pretrained_model_name_or_path,
        train_data_dir,
        output_name,
        output_dir,
        learning_rate,
        text_encoder_lr,
        network_dim,
        network_alpha,
        epoch,
        max_train_steps,
        max_resolution,
        train_batch_size,
        cache_latents,
        cache_latents_to_disk,
        save_model_as,
        save_precision
    ):
        """UIの入力値を既存train_model関数の引数形式に変換"""
        
        # プリセット値をベースに設定
        defaults = MINIMAL_DEFAULT_CONFIG.copy()
        fixed = SDXL_FACE_LORA_FIXED.copy()
        
        # UIからの値で上書き
        ui_values = {
            'pretrained_model_name_or_path': pretrained_model_name_or_path,
            'train_data_dir': train_data_dir,
            'output_name': output_name,
            'output_dir': output_dir,
            'learning_rate': float(learning_rate),
            'epoch': int(epoch),
            'max_train_steps': int(max_train_steps) if int(max_train_steps) > 0 else 0,
            'max_resolution': max_resolution,
            'train_batch_size': int(train_batch_size),
            'cache_latents': cache_latents,
            'cache_latents_to_disk': cache_latents_to_disk,
            'save_model_as': save_model_as,
            'save_precision': save_precision,
            'network_dim': int(network_dim),
            'network_alpha': int(network_alpha),
        }
        
        # LoRA network引数を設定（シンプルなLoRA設定）
        # 注: down_lr_weight/up_lr_weight はブロック単位の学習率制御用で、
        #     SDXLでは9個のブロックに対応したリストが必要。
        #     Text Encoder学習率は text_encoder_lr パラメータで設定済み。
        network_args = ''  # シンプルなLoRA設定（追加引数なし）
        
        # 全設定をマージ
        final_config = {**defaults, **fixed, **ui_values}
        
        # network関連の設定を追加
        final_config['network_args'] = network_args
        final_config['network_module'] = 'networks.lora'
        
        # train_model関数の引数順序に合わせて返す（全121引数）
        return [
            self.headless,  # headless
            False,  # print_only
            # source model section
            final_config['pretrained_model_name_or_path'],
            final_config['v2'],
            final_config['v_parameterization'], 
            final_config['sdxl'],
            final_config['flux1_checkbox'],
            final_config['dataset_config'],
            final_config['save_model_as'],
            final_config['save_precision'],
            final_config['train_data_dir'],
            final_config['output_name'],
            final_config['model_list'],
            final_config['training_comment'],
            # folders section
            final_config['logging_dir'],
            '', # reg_data_dir (正則化画像は使わない)
            final_config['output_dir'],
            # basic training section
            final_config['max_resolution'],
            final_config['learning_rate'],
            final_config['lr_scheduler'],
            final_config['lr_warmup'],
            final_config['lr_warmup_steps'],
            final_config['train_batch_size'],
            final_config['epoch'],
            final_config['save_every_n_epochs'],
            final_config['seed'],
            final_config['cache_latents'],
            final_config['cache_latents_to_disk'],
            final_config['caption_extension'],
            final_config['enable_bucket'],
            final_config['stop_text_encoder_training'],
            final_config['min_bucket_reso'],
            final_config['max_bucket_reso'],
            final_config['max_train_epochs'],
            final_config['max_train_steps'],
            final_config['lr_scheduler_num_cycles'],
            final_config['lr_scheduler_power'],
            final_config['optimizer'],
            final_config['optimizer_args'],
            final_config['lr_scheduler_args'],
            final_config['lr_scheduler_type'],
            final_config['max_grad_norm'],
            # accelerate launch section
            final_config['mixed_precision'],
            final_config['num_cpu_threads_per_process'],
            final_config['num_processes'],
            final_config['num_machines'],
            final_config['multi_gpu'],
            final_config['gpu_ids'],
            final_config['main_process_port'],
            final_config['dynamo_backend'],
            final_config['dynamo_mode'],
            final_config['dynamo_use_fullgraph'],
            final_config['dynamo_use_dynamic'],
            final_config['extra_accelerate_launch_args'],
            # advanced training section  
            final_config['gradient_checkpointing'],
            final_config['fp8_base'],
            final_config['fp8_base_unet'],
            final_config['full_fp16'],
            final_config['highvram'],
            final_config['lowvram'],
            final_config['xformers'],
            final_config['shuffle_caption'],
            final_config['save_state'],
            final_config['save_state_on_train_end'],
            final_config['resume'],
            final_config['prior_loss_weight'],
            final_config['color_aug'],
            final_config['flip_aug'], 
            final_config['masked_loss'],
            final_config['clip_skip'],
            final_config['gradient_accumulation_steps'],
            final_config['mem_eff_attn'],
            final_config['max_token_length'],
            final_config['max_data_loader_n_workers'],
            final_config.get('keep_tokens', 0),
            final_config.get('persistent_data_loader_workers', False),
            final_config.get('bucket_no_upscale', False),
            final_config.get('random_crop', False),
            final_config.get('bucket_reso_steps', 64),
            final_config.get('v_pred_like_loss', 0.0),
            final_config.get('caption_dropout_every_n_epochs', 0),
            final_config.get('caption_dropout_rate', 0.0),
            final_config.get('noise_offset_type', 'Original'),
            final_config.get('noise_offset', 0.0),
            final_config.get('noise_offset_random_strength', 0.0),
            final_config.get('adaptive_noise_scale', 0.0),
            final_config.get('multires_noise_iterations', 0),
            final_config.get('multires_noise_discount', 0.0),
            final_config.get('ip_noise_gamma', 0.0),
            final_config.get('ip_noise_gamma_random_strength', 0.0),
            final_config.get('additional_parameters', ''),
            final_config.get('loss_type', 'l2'),
            final_config.get('huber_schedule', 'snr'),
            final_config.get('huber_c', 0.1),
            final_config.get('huber_scale', 1.0),
            final_config.get('vae_batch_size', 1),
            final_config.get('min_snr_gamma', 0.0),
            final_config.get('save_every_n_steps', 0),
            final_config.get('save_last_n_steps', 0),
            final_config.get('save_last_n_steps_state', False),
            final_config.get('save_last_n_epochs', 0),
            final_config.get('save_last_n_epochs_state', False),
            final_config.get('skip_cache_check', False),
            final_config.get('log_with', ''),
            final_config.get('wandb_api_key', ''),
            final_config.get('wandb_run_name', ''),
            final_config.get('log_tracker_name', ''),
            final_config.get('log_tracker_config', ''),
            final_config.get('log_config', ''),
            final_config.get('scale_v_pred_loss_like_noise_pred', False),
            final_config.get('full_bf16', False),
            final_config.get('min_timestep', 0),
            final_config.get('max_timestep', 1000),
            final_config.get('vae', ''),
            final_config.get('weighted_captions', False),
        ]

def sdxl_simple_tab(headless: bool = False, config: Any = None, use_shell_flag: bool = False):
    """SDXL Simple タブを作成して返す"""
    tab = SDXLSimpleTab(headless=headless, config=config, use_shell_flag=use_shell_flag)
    tab.create_ui()
    return tab