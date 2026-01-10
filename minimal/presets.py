# SDXL Face LoRA Presets
# SDXL顔LoRA用の推奨設定値

# config.tomlの設定を基にした最適化済み設定
SDXL_FACE_LORA_DEFAULTS = {
    # Model Source
    'v2': False,
    'v_parameterization': False,
    'sdxl': True,
    'flux1_checkbox': False,
    'save_model_as': 'safetensors',
    'save_precision': 'fp16',
    'model_list': 'custom',
    'training_comment': 'SDXL Face LoRA - Minimal Interface',
    
    # Training Data
    'max_resolution': '512,512',
    'caption_extension': '.txt',
    'enable_bucket': True,
    'min_bucket_reso': 256,
    'max_bucket_reso': 2048,
    'shuffle_caption': False,
    'stop_text_encoder_training': 0,
    'flip_aug': False,  # 顔LoRAでは非推奨
    'color_aug': False,  # 顔LoRAでは非推奨
    
    # Basic Training
    'learning_rate': 0.0001,  # 1e-4
    'lr_scheduler': 'cosine_with_restarts',
    'lr_scheduler_num_cycles': 3,
    'lr_scheduler_power': 1.0,
    'lr_warmup': 0,
    'lr_warmup_steps': 0,
    'train_batch_size': 1,
    'epoch': 6,
    'max_train_epochs': 0,  # epochを優先
    'max_train_steps': 1600,  # config.tomlの値
    'save_every_n_epochs': 1,
    'seed': 0,
    'cache_latents': True,
    'cache_latents_to_disk': True,  # VRAM節約のため
    
    # Network (LoRA)
    'network_dim': 16,
    'network_alpha': 16,
    'network_module': 'networks.lora',
    'optimizer': 'AdamW8bit',  # メモリ効率化
    'optimizer_args': '',
    'lr_scheduler_args': '',
    'lr_scheduler_type': '',
    'max_grad_norm': 1.0,
    
    # Accelerate Launch
    'mixed_precision': 'fp16',
    'num_cpu_threads_per_process': 1,
    'num_processes': 1,
    'num_machines': 1,
    'multi_gpu': False,
    'gpu_ids': '',
    'main_process_port': 0,
    'dynamo_backend': 'no',
    'dynamo_mode': 'default',
    'dynamo_use_fullgraph': False,
    'dynamo_use_dynamic': False,
    'extra_accelerate_launch_args': '',
    
    # Advanced Training
    'gradient_checkpointing': True,
    'fp8_base': False,
    'fp8_base_unet': False,
    'full_fp16': False,
    'highvram': False,
    'lowvram': False,
    'xformers': True,
    'save_state': True,
    'save_state_on_train_end': False,
    'resume': '',
    'prior_loss_weight': 1.0,
    'masked_loss': False,
    'clip_skip': 2,
    'gradient_accumulation_steps': 1,
    'mem_eff_attn': False,
    'max_token_length': 225,
    'max_data_loader_n_workers': 0,
    
    # Folders (デフォルト値、UIで変更可能)
    'logging_dir': '',
    'reg_data_dir': '',
    'dataset_config': '',  # 使用しない（train_data_dirを使用）
}

# SDXL顔LoRA用の固定設定（変更不可）
SDXL_FACE_LORA_FIXED = {
    'sdxl': True,  # 必ずTrue
    'v2': False,   # SDXLではFalse
    'v_parameterization': False,  # SDXLではFalse
    'flux1_checkbox': False,  # SDXL専用なのでFalse
}

# UIで表示する解像度選択肢
RESOLUTION_CHOICES = [
    '512,512',   # 推奨（顔LoRA用）
    '768,768',
    '1024,1024'
]

# UIで表示するバッチサイズ選択肢
BATCH_SIZE_CHOICES = [1, 2, 4]  # 顔LoRAでは1推奨

# UIで表示する保存形式選択肢
SAVE_MODEL_AS_CHOICES = ['safetensors', 'ckpt']

# UIで表示する保存精度選択肢  
SAVE_PRECISION_CHOICES = ['fp16', 'bf16', 'float']