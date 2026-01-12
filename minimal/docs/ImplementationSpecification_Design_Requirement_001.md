# 実装仕様: Design_Requirement_001.md に基づく実装

## 概要

本ドキュメントは、[Design_Requirement_001.md](Design_Requirement_001.md) で定義された要件に基づく実装仕様を記載します。

## 要件の再確認

**Minimalタブの「Start Training」ボタンは、LoRAタブのTrainingタブの「Start Training」ボタンの挙動を模倣する。**

## 実装方針（重要）

### 重要なポイント

1. **Trainingパラメータ生成（243個、デフォルト値）は実装しない**
   - TrainingタブのUIコンポーネントのデフォルト値は、そのUIコンポーネントから取得する
   - デフォルト値を「生成」するのではなく、Trainingタブの`settings_list`構築ロジックを再利用する

2. **Trainingタブの`settings_list`構築ロジックを関数化して再利用**
   - `kohya_gui/lora_gui.py` 2800行目以降の`settings_list`構築ロジックを関数化
   - UIコンポーネントではなく、パラメータ辞書を受け取るようにする

3. **Minimalタブの16個のパラメータで上書き**
   - Trainingタブのデフォルト値（UIコンポーネントから取得）をベースに
   - Minimalタブで設定した16個の値で上書き

## 実装フロー

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

### ステップ2: Trainingタブの`settings_list`構築ロジックを関数化

`kohya_gui/lora_gui.py` 2800行目以降の`settings_list`構築ロジックを関数化します。

**重要**: この関数は、UIコンポーネントではなく、パラメータ辞書を受け取るようにします。

```python
def build_settings_list_from_params(params: dict) -> list:
    """
    Trainingタブの`settings_list`構築ロジックを関数化
    
    元のロジック（lora_gui.py 2800行目以降）:
    settings_list = [
        source_model.pretrained_model_name_or_path,
        source_model.v2,
        source_model.v_parameterization,
        source_model.sdxl_checkbox,
        ...
    ]
    
    この関数は、UIコンポーネントではなく、パラメータ辞書を受け取る
    
    Args:
        params: パラメータ辞書（243個のパラメータを含む）
        
    Returns:
        list: train_model関数に渡すsettings_list（243個、Trainingタブと同じ順序）
    """
    # Trainingタブのsettings_list構築ロジックと同じ順序で値を取得
    return [
        params.get('pretrained_model_name_or_path'),
        params.get('v2', False),
        params.get('v_parameterization', False),
        params.get('sdxl', True),  # SDXL固定
        params.get('flux1_checkbox', False),
        params.get('dataset_config', ''),
        params.get('save_model_as', 'safetensors'),
        params.get('save_precision', 'fp16'),
        params.get('train_data_dir', ''),
        params.get('output_name', ''),
        params.get('model_list', ''),
        params.get('training_comment', ''),
        params.get('logging_dir', ''),
        params.get('reg_data_dir', ''),
        params.get('output_dir', './outputs'),
        params.get('max_resolution', '512,512'),
        params.get('learning_rate', 0.0001),
        params.get('lr_scheduler', 'cosine'),
        params.get('lr_warmup', 0),
        params.get('lr_warmup_steps', 0),
        params.get('train_batch_size', 1),
        params.get('epoch', 6),
        params.get('save_every_n_epochs', 0),
        params.get('seed', ''),
        params.get('cache_latents', True),
        params.get('cache_latents_to_disk', True),
        # ... 残り218個のパラメータを同じ順序で
    ]
```

**実装場所**: この関数は、`kohya_gui/lora_gui.py` に追加するか、`minimal/` ディレクトリに新しいモジュールとして作成します。

### ステップ3: Trainingタブのデフォルト値を取得

TrainingタブのUIコンポーネントのデフォルト値を取得します。

**重要**: デフォルト値を「生成」するのではなく、TrainingタブのUIコンポーネントから取得します。

```python
def _get_training_defaults(self) -> dict:
    """
    TrainingタブのUIコンポーネントのデフォルト値を取得
    
    注意: デフォルト値を「生成」するのではなく、
    TrainingタブのUIコンポーネント（またはそのデフォルト値）から取得する
    
    Returns:
        dict: Trainingタブのデフォルト値辞書（243個のパラメータ）
    """
    # 方法1: TrainingタブのUIコンポーネントから直接取得（推奨）
    # ただし、MinimalタブではUIコンポーネントを構築しないため、
    # TrainingタブのUIコンポーネントのデフォルト値を参照する必要がある
    
    # 方法2: TrainingタブのUIコンポーネントのデフォルト値をハードコード
    # （TrainingタブのUIコンポーネントの初期値と同じ値を使用）
    
    # 方法3: TrainingタブのUIコンポーネントのデフォルト値を外部から取得
    # （設定ファイルやプリセットから取得）
    
    # 実装例（方法2）:
    defaults = {
        'v2': False,
        'v_parameterization': False,
        'sdxl': True,  # SDXL固定
        'flux1_checkbox': False,
        'dataset_config': '',
        'model_list': '',
        'training_comment': '',
        'logging_dir': '',
        'reg_data_dir': '',
        'lr_scheduler': 'cosine',
        'lr_warmup': 0,
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
        # ... 残り218個のパラメータのデフォルト値
    }
    
    # SDXL顔LoRA用の最適化済みデフォルト値を適用
    from minimal.presets import MINIMAL_DEFAULT_CONFIG, SDXL_FACE_LORA_FIXED
    defaults.update(MINIMAL_DEFAULT_CONFIG)
    defaults.update(SDXL_FACE_LORA_FIXED)
    
    return defaults
```

**注意**: この関数は、TrainingタブのUIコンポーネントのデフォルト値を参照する必要があります。TrainingタブのUIコンポーネントを構築しないため、そのデフォルト値をハードコードするか、設定ファイルから取得する必要があります。

### ステップ4: Minimalパラメータマージ

Trainingタブのデフォルト値に、Minimalタブで設定した16個の値を上書きします。

```python
def _merge_params(self, training_defaults: dict, minimal_params: dict) -> dict:
    """
    Trainingタブのデフォルト値に、Minimalタブで設定した値を上書き
    
    Args:
        training_defaults: Trainingタブのデフォルト値辞書（243個）
        minimal_params: Minimalタブのパラメータ辞書（16個）
        
    Returns:
        dict: マージ後のパラメータ辞書（243個）
    """
    # Trainingタブのデフォルト値に、Minimalタブの値を上書き
    final_params = {**training_defaults, **minimal_params}
    return final_params
```

### ステップ5: settings_list の構築

マージ後のパラメータ辞書から、Trainingタブと同じ順序で`settings_list`を構築します。

```python
def _build_settings_list(self, params: dict) -> list:
    """
    Trainingタブと同じ順序でsettings_listを構築
    
    Args:
        params: マージ後のパラメータ辞書（243個）
        
    Returns:
        list: train_model関数に渡すsettings_list（243個）
    """
    # Trainingタブのsettings_list構築ロジックを関数化したものを使用
    from minimal.utils import build_settings_list_from_params
    return build_settings_list_from_params(params)
```

### ステップ6: train_model() の呼び出し

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
        
        # 2. Trainingタブのデフォルト値を取得（UIコンポーネントから取得、生成しない）
        training_defaults = self._get_training_defaults()
        
        # 3. Minimalパラメータマージ
        final_params = self._merge_params(training_defaults, minimal_params)
        
        # 4. settings_list を構築（Trainingタブと同じ順序）
        settings_list = self._build_settings_list(final_params)
        
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

## 実装上の注意事項

### 1. Trainingタブのデフォルト値の取得方法

TrainingタブのUIコンポーネントのデフォルト値を取得する方法：

- **方法1**: TrainingタブのUIコンポーネントから直接取得（推奨）
  - ただし、MinimalタブではUIコンポーネントを構築しないため、TrainingタブのUIコンポーネントのデフォルト値を参照する必要がある
  - TrainingタブのUIコンポーネントの初期値をハードコードするか、設定ファイルから取得

- **方法2**: TrainingタブのUIコンポーネントのデフォルト値をハードコード
  - TrainingタブのUIコンポーネントの初期値と同じ値を使用
  - `minimal/presets.py` に定義されたデフォルト値を使用

- **方法3**: TrainingタブのUIコンポーネントのデフォルト値を外部から取得
  - 設定ファイルやプリセットから取得

### 2. `settings_list`構築ロジックの関数化

`kohya_gui/lora_gui.py` 2800行目以降の`settings_list`構築ロジックを関数化する際の注意点：

- **順序の維持**: Trainingタブの`settings_list`構築ロジックと同じ順序を維持する必要がある
- **パラメータ名のマッピング**: TrainingタブのUIコンポーネント名と、パラメータ辞書のキー名を正しくマッピングする
- **デフォルト値の処理**: パラメータ辞書に存在しないキーに対しては、適切なデフォルト値を設定する

### 3. パラメータ名のマッピング

TrainingタブのUIコンポーネント名と、パラメータ辞書のキー名のマッピング：

```python
# TrainingタブのUIコンポーネント名 → パラメータ辞書のキー名
MAPPING = {
    'source_model.pretrained_model_name_or_path': 'pretrained_model_name_or_path',
    'source_model.v2': 'v2',
    'source_model.v_parameterization': 'v_parameterization',
    'source_model.sdxl_checkbox': 'sdxl',
    'basic_training.learning_rate': 'learning_rate',
    'basic_training.max_resolution': 'max_resolution',
    # ... 残り238個のマッピング
}
```

### 4. 実装場所

- **`build_settings_list_from_params()` 関数**: 
  - `kohya_gui/lora_gui.py` に追加するか、`minimal/utils.py` に新しいモジュールとして作成
  - Trainingタブの`settings_list`構築ロジックを関数化したもの

- **`_get_training_defaults()` メソッド**: 
  - `minimal/sdxl_simple_tab.py` の`SDXLSimpleTab`クラスに追加

- **`_generate_minimal_params()` メソッド**: 
  - `minimal/sdxl_simple_tab.py` の`SDXLSimpleTab`クラスに追加

- **`_merge_params()` メソッド**: 
  - `minimal/sdxl_simple_tab.py` の`SDXLSimpleTab`クラスに追加

- **`_build_settings_list()` メソッド**: 
  - `minimal/sdxl_simple_tab.py` の`SDXLSimpleTab`クラスに追加

- **`start_training()` メソッド**: 
  - `minimal/sdxl_simple_tab.py` の`SDXLSimpleTab`クラスに既存の実装を置き換え

## 実装チェックリスト

- [ ] `build_settings_list_from_params()` 関数を実装
  - [ ] Trainingタブの`settings_list`構築ロジック（2800行目以降）を関数化
  - [ ] パラメータ辞書を受け取るように変更
  - [ ] Trainingタブと同じ順序を維持

- [ ] `_get_training_defaults()` メソッドを実装
  - [ ] TrainingタブのUIコンポーネントのデフォルト値を取得
  - [ ] SDXL顔LoRA用の最適化済みデフォルト値を適用

- [ ] `_generate_minimal_params()` メソッドを実装
  - [ ] MinimalタブのUI入力値から16個のパラメータを辞書形式で生成

- [ ] `_merge_params()` メソッドを実装
  - [ ] Trainingタブのデフォルト値に、Minimalタブの値を上書き

- [ ] `_build_settings_list()` メソッドを実装
  - [ ] マージ後のパラメータ辞書から、Trainingタブと同じ順序で`settings_list`を構築

- [ ] `start_training()` メソッドを更新
  - [ ] 既存の`_convert_ui_to_train_args()` を削除
  - [ ] 新しい実装フロー（6ステップ）に置き換え

- [ ] テスト
  - [ ] `settings_list`の順序がTrainingタブと同じであることを確認
  - [ ] Minimalタブで設定した値が正しく反映されることを確認
  - [ ] Trainingタブと同じ結果が得られることを確認

## 関連ドキュメント

- **設計要件**: [Design_Requirement_001.md](Design_Requirement_001.md)
- **実装アプローチ**: [AlternativeApproach.md](AlternativeApproach.md)
- **Trainingタブの挙動調査**: [investigation/lora_start_training_flow.md](investigation/lora_start_training_flow.md)
- **settings_list の構築**: `kohya_gui/lora_gui.py` 2800行目以降
