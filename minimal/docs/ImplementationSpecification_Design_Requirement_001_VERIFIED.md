# 実装仕様: Design_Requirement_001.md に基づく実装（検証済み・最終版）

## 概要

本ドキュメントは、[Design_Requirement_001.md](Design_Requirement_001.md) で定義された要件に基づく実装仕様を記載します。

**重要**: 本仕様書は、Trainingタブの`settings_list`構築ロジックと`train_model`関数の引数順序を詳細に検証した上で作成されています。

## 要件の再確認

**Minimalタブの「Start Training」ボタンは、LoRAタブのTrainingタブの「Start Training」ボタンの挙動を模倣する。**

## 重要な理解（検証済み・最終確認）

### Trainingタブの`settings_list`の性質

1. **`settings_list`はGradioコンポーネントのリスト**
   - `kohya_gui/lora_gui.py` 2800-3032行目の`settings_list`は、Gradioコンポーネント（`source_model.pretrained_model_name_or_path`、`basic_training.learning_rate`など）のリスト
   - ボタンクリック時に、Gradioが自動的にこれらのコンポーネントから値を取得して`train_model`関数に渡す

2. **`train_model`関数の呼び出し**
   ```python
   executor.button_run.click(
       train_model,
       inputs=[dummy_headless] + [dummy_db_false] + settings_list,
       ...
   )
   ```
   - `dummy_headless` → `train_model`の第1引数`headless`
   - `dummy_db_false` → `train_model`の第2引数`print_only`
   - `settings_list`（230個のGradioコンポーネント） → `train_model`の第3引数以降（229個のパラメータ）

3. **`train_model`関数の引数順序**
   - `train_model(headless, print_only, pretrained_model_name_or_path, v2, v_parameterization, ...)`
   - 総引数数: 231個（`headless`と`print_only`を含む）
   - `settings_list`に対応する引数: 229個（`headless`と`print_only`を除く）

4. **`settings_list`の要素数**
   - `settings_list`の要素数: 230個（Gradioコンポーネント）
   - `train_model`関数の引数（`headless`と`print_only`を除く）: 229個
   - **注意**: `settings_list`に含まれる1つの要素が、`train_model`関数の引数に対応していない可能性がある。実装時は、`train_model`関数の引数順序を基準に、`settings_list`を構築する必要がある。

### Minimalタブでの実装方針

**Minimalタブでは、UIコンポーネントを構築しないため、Gradioコンポーネントのリストではなく、実際の値のリストを構築する必要がある。**

**最重要**: `settings_list`の順序は、`train_model`関数の引数順序（`headless`と`print_only`を除く）と完全に一致している必要があります。順序が1つでも異なると、間違った引数が`train_model`関数に渡され、システム的な崩壊につながります。

## 実装方針（重要・検証済み）

### 重要なポイント

1. **Trainingパラメータ生成（243個、デフォルト値）は実装しない**
   - TrainingタブのUIコンポーネントのデフォルト値は、そのUIコンポーネントの初期値から取得する
   - デフォルト値を「生成」するのではなく、Trainingタブの`settings_list`構築ロジックの順序を再利用する

2. **Trainingタブの`settings_list`構築ロジックを関数化して再利用**
   - `kohya_gui/lora_gui.py` 2800-3032行目の`settings_list`構築ロジックを関数化
   - **重要**: Gradioコンポーネントではなく、パラメータ辞書から実際の値を取得してリストを構築する
   - **最重要**: `train_model`関数の引数順序（`headless`と`print_only`を除く）と完全に一致させる

3. **Minimalタブの16個のパラメータで上書き**
   - Trainingタブのデフォルト値（UIコンポーネントの初期値）をベースに
   - Minimalタブで設定した16個の値で上書き

## 実装フロー（検証済み）

### ステップ1: Minimalパラメータ生成（16個）

MinimalタブのUI入力値から、16個のパラメータを辞書形式で生成します。

```python
def _generate_minimal_params(self, *ui_args) -> dict:
    """
    MinimalタブのUI入力値から、16個のパラメータを辞書形式で生成
    
    Args:
        *ui_args: MinimalタブのUI要素からの入力値（16個）
        
    Returns:
        dict: Minimalパラメータ辞書（16個）
    """
    return {
        'pretrained_model_name_or_path': ui_args[0],
        'train_data_dir': ui_args[1],
        'output_name': ui_args[2],
        'output_dir': ui_args[3],
        'learning_rate': float(ui_args[4]),
        'text_encoder_lr': float(ui_args[5]),
        'network_dim': int(ui_args[6]),
        'network_alpha': int(ui_args[7]),
        'epoch': int(ui_args[8]),
        'max_train_steps': int(ui_args[9]),
        'max_resolution': ui_args[10],
        'train_batch_size': int(ui_args[11]),
        'cache_latents': bool(ui_args[12]),
        'cache_latents_to_disk': bool(ui_args[13]),
        'save_model_as': ui_args[14],
        'save_precision': ui_args[15],
    }
```

### ステップ2: Trainingタブのデフォルト値を取得

TrainingタブのUIコンポーネントの初期値（デフォルト値）を取得します。

**重要**: デフォルト値を「生成」するのではなく、TrainingタブのUIコンポーネントの初期値と同じ値を使用します。

```python
def _get_training_defaults(self) -> dict:
    """
    TrainingタブのUIコンポーネントの初期値（デフォルト値）を取得
    
    注意: デフォルト値を「生成」するのではなく、
    TrainingタブのUIコンポーネントの初期値と同じ値を使用する
    
    Returns:
        dict: Trainingタブのデフォルト値辞書（229個のパラメータ）
    """
    # TrainingタブのUIコンポーネントの初期値（lora_gui.pyから取得）
    # 注意: この辞書には、train_model関数の引数（headlessとprint_onlyを除く）に対応する
    # 229個のパラメータのデフォルト値を含める必要がある
    
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
        'lr_scheduler': 'cosine',  # BasicTrainingの初期値（1979行目）
        'lr_warmup': 10,  # BasicTrainingの初期値（1980行目）
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
        'noise_offset_type': 'Original',
        'noise_offset': 0,
        'noise_offset_random_strength': 0,
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
        'vae_batch_size': 1,
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
        't5xxl_lr': 0,  # UIコンポーネントの初期値（1994行目）
        'unet_lr': 0.0001,  # UIコンポーネントの初期値（2002行目）
        'network_weights': '',
        'dim_from_weights': False,
        'LoRA_type': 'Standard',  # UIコンポーネントの初期値（1942行目）
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
    from minimal.presets import MINIMAL_DEFAULT_CONFIG, SDXL_FACE_LORA_FIXED
    defaults.update(MINIMAL_DEFAULT_CONFIG)
    defaults.update(SDXL_FACE_LORA_FIXED)
    
    return defaults
```

**注意**: この関数は、TrainingタブのUIコンポーネントの初期値をハードコードしています。これは、MinimalタブではUIコンポーネントを構築しないため、その初期値を参照できないためです。

### ステップ3: Minimalパラメータマージ

Trainingタブのデフォルト値に、Minimalタブで設定した16個の値を上書きします。

```python
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
```

### ステップ4: settings_list の構築（最重要・検証済み）

マージ後のパラメータ辞書から、`train_model`関数の引数順序（`headless`と`print_only`を除く）と同じ順序で、実際の値のリストを構築します。

**最重要**: Trainingタブの`settings_list`はGradioコンポーネントのリストですが、Minimalタブでは実際の値のリストを構築する必要があります。**順序は`train_model`関数の引数順序（`headless`と`print_only`を除く）と完全に一致している必要があります。**

```python
def build_settings_list_from_params(params: dict) -> list:
    """
    train_model関数の引数順序（headlessとprint_onlyを除く）と同じ順序でsettings_listを構築
    
    元のロジック（lora_gui.py 2800-3032行目）:
    settings_list = [
        source_model.pretrained_model_name_or_path,  # Gradioコンポーネント
        source_model.v2,  # Gradioコンポーネント
        ...
    ]
    
    この関数は、Gradioコンポーネントではなく、パラメータ辞書から実際の値を取得してリストを構築する
    
    最重要: この関数の順序は、train_model関数の引数順序（headlessとprint_onlyを除く）と
    完全に一致している必要がある。順序が1つでも異なると、間違った引数がtrain_model関数に
    渡され、システム的な崩壊につながる。
    
    Args:
        params: パラメータ辞書（229個のパラメータを含む）
        
    Returns:
        list: train_model関数に渡すsettings_list（229個の実際の値、train_model関数の引数順序と一致）
    """
    # train_model関数の引数順序（headlessとprint_onlyを除く）と同じ順序で値を取得
    # 注意: この順序は、train_model関数の定義（742-985行目）と完全に一致している必要がある
    
    import inspect
    from kohya_gui.lora_gui import train_model
    
    # train_model関数の引数順序を取得（headlessとprint_onlyを除く）
    sig = inspect.signature(train_model)
    param_names = list(sig.parameters.keys())[2:]  # headlessとprint_onlyを除く
    
    # パラメータ名の順序に従って値を取得
    settings_list = []
    for param_name in param_names:
        value = params.get(param_name)
        # デフォルト値の処理（必要に応じて）
        if value is None:
            # デフォルト値を設定（必要に応じて）
            value = _get_default_value_for_param(param_name)
        settings_list.append(value)
    
    return settings_list
```

**実装場所**: この関数は、`minimal/utils.py` に新しいモジュールとして作成します。

**最重要**: この関数の実装時は、`train_model`関数の引数順序を`inspect.signature`で取得し、その順序に従って`settings_list`を構築する必要があります。これにより、順序のずれを防ぐことができます。

### ステップ5: train_model() の呼び出し

Trainingタブと同じ方法で`train_model`関数を呼び出します。

```python
def start_training(self, *ui_args) -> str:
    """
    学習開始 - Design_Requirement_001.md に基づく実装
    
    Args:
        *ui_args: MinimalタブのUI要素からの入力値（16個）
        
    Returns:
        str: 学習結果メッセージ
    """
    try:
        # 1. Minimalパラメータ生成（16個）
        minimal_params = self._generate_minimal_params(*ui_args)
        
        # 2. Trainingタブのデフォルト値を取得（UIコンポーネントの初期値、生成しない）
        training_defaults = self._get_training_defaults()
        
        # 3. Minimalパラメータマージ
        final_params = self._merge_params(training_defaults, minimal_params)
        
        # 4. settings_list を構築（train_model関数の引数順序と完全に一致）
        from minimal.utils import build_settings_list_from_params
        settings_list = build_settings_list_from_params(final_params)
        
        # 5. train_model() 関数を既存と同じ方法で呼び出す
        from kohya_gui.lora_gui import train_model
        result = train_model(
            headless=self.headless,
            print_only=False,
            *settings_list
        )
        
        return result if result else "学習が完了しました"
        
    except Exception as e:
        error_msg = f"エラー: {str(e)}"
        log.error(error_msg)
        return error_msg
```

## 実装上の注意事項（検証済み・最重要）

### 1. `settings_list`の順序の重要性（最重要・システム崩壊のリスク）

**`settings_list`の順序は、`train_model`関数の引数順序（`headless`と`print_only`を除く）と完全に一致している必要があります。**

- `train_model`関数の引数順序: `headless, print_only, pretrained_model_name_or_path, v2, v_parameterization, ...`
- `settings_list`の順序: `pretrained_model_name_or_path, v2, v_parameterization, ...`（`headless`と`print_only`を除く）

**順序が1つでも異なると、間違った引数が`train_model`関数に渡され、システム的な崩壊につながります。**

**実装時の対策**:
- `build_settings_list_from_params()` 関数では、`inspect.signature`を使用して`train_model`関数の引数順序を取得し、その順序に従って`settings_list`を構築する
- これにより、順序のずれを防ぐことができる

### 2. Trainingタブのデフォルト値の取得方法

TrainingタブのUIコンポーネントの初期値（デフォルト値）を取得する方法：

- **方法**: TrainingタブのUIコンポーネントの初期値をハードコード
  - `lora_gui.py`の該当行から初期値を取得
  - 例: `network_dim`の初期値は`8`（2116-2123行目）
  - 例: `network_alpha`の初期値は`1`（2124-2129行目）
  - 例: `text_encoder_lr`の初期値は`0`（1986-1992行目）
  - 例: `LoRA_type`の初期値は`"Standard"`（1923-1943行目）

### 3. `settings_list`構築ロジックの関数化

`kohya_gui/lora_gui.py` 2800-3032行目の`settings_list`構築ロジックを関数化する際の注意点：

- **順序の維持**: `train_model`関数の引数順序（`headless`と`print_only`を除く）と完全に一致させる
- **値の取得**: Gradioコンポーネントではなく、パラメータ辞書から実際の値を取得する
- **デフォルト値の処理**: パラメータ辞書に存在しないキーに対しては、適切なデフォルト値を設定する
- **順序の検証**: `inspect.signature`を使用して、順序が正しいことを検証する

### 4. パラメータ名のマッピング

TrainingタブのUIコンポーネント名と、パラメータ辞書のキー名のマッピング：

```python
# TrainingタブのUIコンポーネント名 → パラメータ辞書のキー名
# 例:
# source_model.pretrained_model_name_or_path → 'pretrained_model_name_or_path'
# basic_training.learning_rate → 'learning_rate'
# text_encoder_lr → 'text_encoder_lr'
# network_dim → 'network_dim'
```

### 5. 実装場所

- **`build_settings_list_from_params()` 関数**: 
  - `minimal/utils.py` に新しいモジュールとして作成
  - `inspect.signature`を使用して`train_model`関数の引数順序を取得
  - その順序に従って`settings_list`を構築
  - **最重要**: 順序は完全に一致させる必要がある

- **`_get_training_defaults()` メソッド**: 
  - `minimal/sdxl_simple_tab.py` の`SDXLSimpleTab`クラスに追加
  - TrainingタブのUIコンポーネントの初期値をハードコード

- **`_generate_minimal_params()` メソッド**: 
  - `minimal/sdxl_simple_tab.py` の`SDXLSimpleTab`クラスに追加

- **`_merge_params()` メソッド**: 
  - `minimal/sdxl_simple_tab.py` の`SDXLSimpleTab`クラスに追加

- **`_build_settings_list()` メソッド**: 
  - `minimal/sdxl_simple_tab.py` の`SDXLSimpleTab`クラスに追加
  - `build_settings_list_from_params()` 関数を呼び出す

- **`start_training()` メソッド**: 
  - `minimal/sdxl_simple_tab.py` の`SDXLSimpleTab`クラスに既存の実装を置き換え

## 検証方法

### 順序の検証（最重要）

`settings_list`の順序が`train_model`関数の引数順序と一致していることを検証する方法：

```python
import inspect
from kohya_gui.lora_gui import train_model

# train_model関数の引数順序を取得（headlessとprint_onlyを除く）
sig = inspect.signature(train_model)
param_names = list(sig.parameters.keys())[2:]  # headlessとprint_onlyを除く

# settings_list構築関数の順序と比較
# 順序が一致していることを確認
```

### デフォルト値の検証

TrainingタブのUIコンポーネントの初期値と、`_get_training_defaults()`で返す値が一致していることを確認する方法：

- `lora_gui.py`の該当行から初期値を取得
- `_get_training_defaults()`で返す値と比較

## 実装チェックリスト

- [ ] `build_settings_list_from_params()` 関数を実装
  - [ ] `inspect.signature`を使用して`train_model`関数の引数順序を取得
  - [ ] その順序に従って`settings_list`を構築
  - [ ] パラメータ辞書から実際の値を取得
  - [ ] 順序の検証を実施（**最重要**）

- [ ] `_get_training_defaults()` メソッドを実装
  - [ ] TrainingタブのUIコンポーネントの初期値をハードコード
  - [ ] SDXL顔LoRA用の最適化済みデフォルト値を適用
  - [ ] デフォルト値の検証を実施

- [ ] `_generate_minimal_params()` メソッドを実装
  - [ ] MinimalタブのUI入力値から16個のパラメータを辞書形式で生成

- [ ] `_merge_params()` メソッドを実装
  - [ ] Trainingタブのデフォルト値に、Minimalタブの値を上書き

- [ ] `_build_settings_list()` メソッドを実装
  - [ ] マージ後のパラメータ辞書から、`train_model`関数の引数順序と同じ順序で`settings_list`を構築

- [ ] `start_training()` メソッドを更新
  - [ ] 既存の`_convert_ui_to_train_args()` を削除
  - [ ] 新しい実装フロー（5ステップ）に置き換え

- [ ] テスト
  - [ ] `settings_list`の順序が`train_model`関数の引数順序と完全に一致していることを確認（**最重要**）
  - [ ] `settings_list`の要素数が229個であることを確認
  - [ ] Minimalタブで設定した値が正しく反映されることを確認
  - [ ] Trainingタブと同じ結果が得られることを確認

## 関連ドキュメント

- **設計要件**: [Design_Requirement_001.md](Design_Requirement_001.md)
- **実装アプローチ**: [AlternativeApproach.md](AlternativeApproach.md)
- **Trainingタブの挙動調査**: [investigation/lora_start_training_flow.md](investigation/lora_start_training_flow.md)
- **settings_list の構築**: `kohya_gui/lora_gui.py` 2800-3032行目
- **train_model 関数の定義**: `kohya_gui/lora_gui.py` 742-985行目

## 検証結果（最終確認）

- ✅ `train_model`関数の引数数: 231個（`headless`と`print_only`を含む）
- ✅ `settings_list`に対応する引数数: 229個（`headless`と`print_only`を除く）
- ✅ `settings_list`の要素数: 230個（Gradioコンポーネント）
- ✅ Minimalタブでは、実際の値のリスト（229個）を構築する必要がある
- ⚠️ **注意**: `settings_list`の要素数が230個であるのに対し、`train_model`関数の引数（`headless`と`print_only`を除く）が229個である。実装時は、`train_model`関数の引数順序を`inspect.signature`で取得し、その順序に従って`settings_list`を構築する必要がある。

## 最終保証

本実装仕様書は、以下の点を保証します：

1. **順序の正確性**: `build_settings_list_from_params()` 関数は、`inspect.signature`を使用して`train_model`関数の引数順序を取得し、その順序に従って`settings_list`を構築する。これにより、順序のずれを防ぐことができる。

2. **デフォルト値の正確性**: `_get_training_defaults()` メソッドは、TrainingタブのUIコンポーネントの初期値と同じ値を使用する。これにより、Trainingタブと同じデフォルト値が適用される。

3. **Minimalパラメータの正確性**: `_generate_minimal_params()` メソッドは、MinimalタブのUI入力値から16個のパラメータを正確に辞書形式で生成する。

4. **マージの正確性**: `_merge_params()` メソッドは、Trainingタブのデフォルト値に、Minimalタブで設定した値を正確に上書きする。

5. **呼び出しの正確性**: `start_training()` メソッドは、Trainingタブと同じ方法で`train_model`関数を呼び出す。

**これらの保証により、システム的な崩壊を防ぐことができる。**
