import gradio as gr
import os
from pathlib import Path
from typing import Any
import logging

# Minimal用プリセット設定を読み込み
from minimal.presets import (
    SDXL_FACE_LORA_DEFAULTS,
    SDXL_FACE_LORA_FIXED,
    RESOLUTION_CHOICES,
    BATCH_SIZE_CHOICES,
    SAVE_MODEL_AS_CHOICES,
    SAVE_PRECISION_CHOICES
)

log = logging.getLogger(__name__)

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
                        value="",
                        interactive=True,
                        scale=3
                    )
                    model_file_button = gr.Button(
                        f"{folder_symbol}",
                        elem_id="model_file_button",
                        scale=1,
                        size="sm"
                    )
                
                with gr.Row():
                    self.save_model_as = gr.Dropdown(
                        label="Save trained model as",
                        choices=SAVE_MODEL_AS_CHOICES,
                        value=SDXL_FACE_LORA_DEFAULTS['save_model_as']
                    )
                    self.save_precision = gr.Dropdown(
                        label="Save precision", 
                        choices=SAVE_PRECISION_CHOICES,
                        value=SDXL_FACE_LORA_DEFAULTS['save_precision']
                    )
            
            # Training Data
            with gr.Accordion("Training Data", open=True):
                with gr.Row():
                    self.train_data_dir = gr.Textbox(
                        label="Image folder",
                        placeholder="学習画像が含まれるフォルダ",
                        value="",
                        interactive=True,
                        scale=3
                    )
                    image_folder_button = gr.Button(
                        f"{folder_symbol}",
                        elem_id="image_folder_button",
                        scale=1,
                        size="sm"
                    )
                
                with gr.Row():
                    self.max_resolution = gr.Dropdown(
                        label="Resolution",
                        choices=RESOLUTION_CHOICES,
                        value=SDXL_FACE_LORA_DEFAULTS['max_resolution'],
                        info="学習解像度（顔LoRAは512x512推奨）"
                    )
                    self.train_batch_size = gr.Dropdown(
                        label="Batch size",
                        choices=BATCH_SIZE_CHOICES,
                        value=SDXL_FACE_LORA_DEFAULTS['train_batch_size'],
                        info="バッチサイズ（1推奨）"
                    )
            
            # Training Parameters  
            with gr.Accordion("Training Parameters", open=True):
                with gr.Row():
                    self.learning_rate = gr.Textbox(
                        label="Learning rate",
                        value=str(SDXL_FACE_LORA_DEFAULTS['learning_rate']),
                        info="学習率（U-Net用）"
                    )
                    self.text_encoder_lr = gr.Textbox(
                        label="Text encoder learning rate",
                        value=str(SDXL_FACE_LORA_DEFAULTS['learning_rate'] * 0.5),  # 半分程度
                        info="Text Encoder学習率"
                    )
                
                with gr.Row():
                    self.network_dim = gr.Number(
                        label="LoRA Rank (dim)",
                        value=SDXL_FACE_LORA_DEFAULTS['network_dim'],
                        minimum=1,
                        maximum=128,
                        step=1,
                        info="LoRAの次元数"
                    )
                    self.network_alpha = gr.Number(
                        label="LoRA Alpha",
                        value=SDXL_FACE_LORA_DEFAULTS['network_alpha'],
                        minimum=1,
                        maximum=128,
                        step=1,
                        info="LoRAのアルファ値"
                    )
                
                with gr.Row():
                    self.epoch = gr.Number(
                        label="Epochs",
                        value=SDXL_FACE_LORA_DEFAULTS['epoch'],
                        minimum=1,
                        maximum=100,
                        step=1
                    )
                    self.max_train_steps = gr.Number(
                        label="Max train steps",
                        value=SDXL_FACE_LORA_DEFAULTS['max_train_steps'],
                        minimum=0,
                        step=100,
                        info="0 = epoch数のみ使用"
                    )
                
                with gr.Row():
                    self.cache_latents = gr.Checkbox(
                        label="Cache latents",
                        value=SDXL_FACE_LORA_DEFAULTS['cache_latents'],
                        info="latentsをキャッシュして高速化"
                    )
                    self.cache_latents_to_disk = gr.Checkbox(
                        label="Cache latents to disk",
                        value=SDXL_FACE_LORA_DEFAULTS['cache_latents_to_disk'],
                        info="ディスクキャッシュでVRAM節約"
                    )
            
            # Output
            with gr.Accordion("Output", open=True):
                with gr.Row():
                    self.output_name = gr.Textbox(
                        label="Output name",
                        placeholder="character_name_lora",
                        value="",
                        info="出力するLoRAモデルの名前"
                    )
                
                with gr.Row():
                    self.output_dir = gr.Textbox(
                        label="Output folder",
                        placeholder="出力フォルダ",
                        value="./outputs",
                        scale=3
                    )
                    output_folder_button = gr.Button(
                        f"{folder_symbol}",
                        elem_id="output_folder_button",
                        scale=1,
                        size="sm"
                    )
            
            # Training Control
            with gr.Accordion("Training", open=True):
                with gr.Row():
                    self.train_button = gr.Button(
                        "Start training",
                        variant="primary",
                        scale=2
                    )
                    self.stop_button = gr.Button(
                        "Stop training",
                        variant="stop",
                        scale=1
                    )
                
                self.output_log = gr.Textbox(
                    label="Training output",
                    value="",
                    lines=15,
                    max_lines=30,
                    interactive=False,
                    show_copy_button=True
                )
            
            # イベント接続
            self.train_button.click(
                fn=self.start_training,
                inputs=self._get_all_inputs(),
                outputs=[self.output_log],
                show_progress=True
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
        学習開始（既存のtrain_model関数を呼び出し）
        UIの値を既存関数の引数形式に変換して渡す
        """
        try:
            # 入力検証
            if not pretrained_model_name_or_path:
                return "エラー: チェックポイントパスが必要です"
            if not train_data_dir or not os.path.exists(train_data_dir):
                return "エラー: 有効な画像フォルダが必要です"
            if not output_name:
                return "エラー: 出力名が必要です"
            if not output_dir:
                return "エラー: 出力フォルダが必要です"
            
            # 既存のtrain_model関数をインポート
            from kohya_gui.lora_gui import train_model
            
            # UIパラメータを既存関数の引数形式に変換
            args = self._convert_ui_to_train_args(
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
            
            # 既存のtrain_model関数を呼び出し
            result = train_model(*args)
            
            return result if result else "学習が完了しました"
            
        except Exception as e:
            error_msg = f"エラー: {str(e)}"
            log.error(error_msg)
            return error_msg
    
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
        defaults = SDXL_FACE_LORA_DEFAULTS.copy()
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
        
        # LoRA network引数を設定
        # Text Encoder学習率の設定
        if float(text_encoder_lr) != float(learning_rate):
            # 異なる学習率を使用する場合
            network_args = f'conv_dim={int(network_dim)} conv_alpha={int(network_alpha)} '
            network_args += f'down_lr_weight={float(text_encoder_lr)} up_lr_weight={float(learning_rate)}'
        else:
            # 同じ学習率の場合はシンプルに
            network_args = ''
        
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