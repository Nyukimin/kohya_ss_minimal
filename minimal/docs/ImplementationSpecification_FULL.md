# SDXL Face LoRA Minimal Tab Implementation Specification (FULL)
**Version:** FULL (統合版)  
**Date:** 2026-01-11  
**Status:** 最新設計思想反映版

## 概要

本仕様書は、`kohya_ss` に **SDXL顔LoRA作成に特化した簡易UIタブ**を追加するための完全な実装指針を定めます。

本タブの目的は以下です：

* SDXL顔LoRA作成時に **毎回触る必要のある最小限のパラメータのみをUI化**する
* repeat や caption など、**GUI外ルール依存による事故を防止**する
* kohya-ss 本体の学習ロジックを変更せず、**GUI拡張として完結**させる
* 将来的に **容易に削除・無効化できる設計**とする

## 1. 設計思想（重要）

### 1.1 基本設計思想

**「最低限のUIでTrainingを開始する」**

- Minimalタブは、必要最小限のパラメータのみをユーザーに入力させる
- 残りのパラメータは、SDXL顔LoRA用の最適化されたデフォルト値を使用
- 既存のTrainingタブの実装を最大限活用し、Minimalタブの変更は最小限に

### 1.2 「Start Training」ボタンの挙動（核心設計思想）

**Minimalタブの「Start Training」ボタンは、LoRAタブのTrainingタブの「Start Training」ボタンの挙動を模倣する。**

これは、Minimalタブの設計思想を実現するための重要な要件です。

#### 設計思想の根拠

1. **一貫性**: Trainingタブと同じ実装パターンを使用することで、コードの一貫性が保たれる
2. **保守性**: `train_model` 関数のシグネチャが変更されても、自動的に対応される
3. **理解しやすさ**: 既存のTrainingタブと同じ実装パターンなので、他の開発者も理解しやすい
4. **メンテナンス性**: 手動マッピングの更新が不要
5. **処理フローの明確化**: Trainingタブの処理フローを分解し、Minimalタブは「パラメータ生成部分」のみを置き換える

### 1.3 本タブの位置づけ

* 新しい学習方式を追加するものではない
* **既存の kohya-ss 学習方式を安全に使うための補助UI**
* **GUI拡張レイヤ**にのみ存在する
* 学習自体は **既存の kohya-ss の仕組みをそのまま使う**

つまり、

> 「新しい学習方式を追加した」のではなく
> 「既存の学習方式を、間違いにくいUIで包んだ」

という位置づけです。

## 2. 変更範囲の制約

### 2.1 変更範囲の制約

* `train_network.py` 等の学習コアには **一切手を入れない**
* upstream の改造は **GUI起点に限定**
* 独自実装は `minimal/` ディレクトリ配下に閉じる

### 2.2 本体統合（最小限変更）

**ファイル**: `kohya_gui/lora_gui.py` 3102-3111行目

```python
# Add SDXL Simple tab
with gr.Tab("Minimal"):
    try:
        from minimal.sdxl_simple_tab import sdxl_simple_tab
        sdxl_simple_tab(headless=headless, config=config, use_shell_flag=use_shell)
    except ImportError:
        gr.Markdown("**SDXL Simple tab not available**")
        gr.Markdown("The minimal SDXL training interface is not installed.")
    except Exception as e:
        gr.Markdown(f"**Error loading SDXL Simple tab**: {str(e)}")
```

**変更行数**: 8行のみ（エラーハンドリング含む）

## 3. ディレクトリ構成

```
kohya_ss_minimal/
├── kohya_gui/
│   └── lora_gui.py          # [修正] Minimalタブを追加（8行のみ）
└── minimal/                 # [新規] 全機能をここに実装
    ├── __init__.py
    ├── config.toml          # ユーザー設定ファイル（自動更新）
    ├── presets.py           # SDXL顔LoRA最適化プリセット
    ├── sdxl_simple_tab.py   # メインUI実装
    ├── README.md            # プロジェクト説明
    └── docs/                # ドキュメント
        ├── Specification_001.md
        ├── ImplementationSpecification_FULL.md  # 本ファイル
        ├── Design_Requirement_001.md
        ├── AlternativeApproach.md
        └── investigation/
            ├── lora_start_training_flow.md
            └── process_startup_flow.md
```

※ `minimal/` を削除すれば機能ごと消える構成。

## 4. タブUI仕様

### 4.1 対象スコープ

* SDXL 専用
* 顔LoRA前提
* 単一 dataset / subset

### 4.2 UI項目一覧（16個のパラメータ）

#### Model Source

* **SDXL Checkpoint** (Textbox + Dropdown)
  - `pretrained_model_name_or_path`
  - 例: `E:/Models/SDXL/harukiMIX_illustrious_v40.safetensors`

* **Save model as** (Dropdown)
  - `save_model_as`
  - 選択肢: `safetensors`, `ckpt`
  - デフォルト: `safetensors`

* **Save precision** (Dropdown)
  - `save_precision`
  - 選択肢: `fp16`, `bf16`, `float`
  - デフォルト: `fp16`

#### Training Data

* **Image folder** (Textbox)
  - `train_data_dir`
  - 例: `E:/LoRA/training_data/SATOMI`

* **Resolution** (Dropdown)
  - `max_resolution`
  - 選択肢: `512,512`, `768,768`, `1024,1024`
  - デフォルト: `512,512`

* **Train batch size** (Number)
  - `train_batch_size`
  - デフォルト: `1`

#### Training Parameters

* **Learning rate (U-Net)** (Number)
  - `learning_rate`
  - デフォルト: `0.0001` (1e-4)

* **Text Encoder LR** (Textbox)
  - `text_encoder_lr`
  - デフォルト: `0.00005` (learning_rateの半分、指数表記ではなく小数表記で表示)

* **LoRA Rank (dim)** (Number)
  - `network_dim`
  - デフォルト: `16`

* **LoRA Alpha** (Number)
  - `network_alpha`
  - デフォルト: `16`

* **Epoch** (Number)
  - `epoch`
  - デフォルト: `6`

* **Max train steps** (Number)
  - `max_train_steps`
  - デフォルト: `1600`

* **Cache latents** (Checkbox)
  - `cache_latents`
  - デフォルト: `True`

* **Cache latents to disk** (Checkbox)
  - `cache_latents_to_disk`
  - デフォルト: `False`（デフォルトOFF、ユーザーが変更した値は保持）

#### Output Settings

* **Output name** (Textbox)
  - `output_name`
  - 例: `SATOMI_001`

* **Output folder** (Textbox)
  - `output_dir`
  - デフォルト: `./outputs`

### 4.3 UI構成（Accordion形式）

```python
with gr.Tab("Minimal"):
    with gr.Accordion("Model Source", open=True):
        # SDXL Checkpoint, Save model as, Save precision
    
    with gr.Accordion("Training Data", open=True):
        # Image folder, Resolution, Train batch size
    
    with gr.Accordion("Caption Generation", open=False):
        # Caption text (固定キャプションテキスト入力)
        # Overwrite existing captions (チェックボックス)
        # Generate caption files ボタン
        # Caption generation result (結果表示)
        # 注意: 画像フォルダ（Image folder）を自動的に使用
    
    with gr.Accordion("Training Parameters", open=True):
        # Learning rate, Text Encoder LR, LoRA Rank/Alpha, Epoch, Max train steps
        # Cache latents, Cache latents to disk
    
    with gr.Accordion("Output Settings", open=True):
        # Output name, Output folder
    
    with gr.Accordion("Training", open=True):
        # Start training ボタン, Save Config ボタン, ログ表示
```

## 5. 学習実行時の処理フロー（核心実装）

### 5.1 設計思想

**Minimalタブの「Start Training」ボタンは、LoRAタブのTrainingタブの「Start Training」ボタンの挙動を模倣する。**

Trainingタブの「Start Training」から学習プロセス開始までの処理フローは、[investigation/lora_start_training_flow.md](investigation/lora_start_training_flow.md) に詳細が記載されています。

### 5.2 Trainingタブの処理フロー（参照）

**ファイル**: `kohya_gui/lora_gui.py` 3081-3086行目

```python
executor.button_run.click(
    train_model,
    inputs=[dummy_headless] + [dummy_db_false] + settings_list,
    outputs=[executor.button_run, executor.button_stop_training, run_state],
    show_progress=False,
)
```

**処理フロー**:
1. **ボタンクリック** → `train_model` 関数が呼び出される
2. **パラメータ受け取り** → `settings_list` に含まれる243個のパラメータが `train_model` 関数に渡される
3. **train_model関数内の処理**:
   - 実行中チェック
   - バリデーション処理（LRスケジューラー、オプティマイザー、パス検証など）
   - 設定の計算と準備（max_train_steps、lr_warmup_steps など）
   - コマンドの構築（Accelerateコマンド、TOML設定ファイル生成など）
   - 設定ファイル保存（TOML、JSON）
   - プロセス起動（`subprocess.Popen()`）

**重要なポイント**:
- `settings_list` は `lora_gui.py` 2800行目以降で構築される
- `settings_list` の順序は `train_model` 関数の引数の順序と一致している必要がある
- `train_model` 関数は243個の引数を受け取る

### 5.3 Minimalタブの処理フロー（実装要件）

Minimalタブの「Start Training」ボタン押下時の処理フロー：

#### ステップ1: Minimalタブの「Start Training」押下

- MinimalタブのUIから16個のパラメータを取得
- UI入力値を検証（必須項目、パス存在確認、数値範囲確認など）

#### ステップ2: Minimalパラメータ生成

- MinimalタブのUI入力値から、16個のパラメータを辞書形式で生成
- 例: `pretrained_model_name_or_path`, `train_data_dir`, `output_name`, `output_dir`, `learning_rate`, `text_encoder_lr`, `network_dim`, `network_alpha`, `epoch`, `max_train_steps`, `max_resolution`, `train_batch_size`, `cache_latents`, `cache_latents_to_disk`, `save_model_as`, `save_precision`

```python
minimal_params = {
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

#### ステップ3: Trainingパラメータ生成

- 既存のTrainingタブと同じように、全243個のパラメータをデフォルト値で生成
- Trainingタブの `settings_list` 構築ロジック（`kohya_gui/lora_gui.py` 2800行目以降）と同じ方法で、デフォルト値を生成
- SDXL顔LoRA用の最適化済みデフォルト値を使用

```python
# 方法1: プリセット値から直接生成（推奨）
from minimal.presets import MINIMAL_DEFAULT_CONFIG, SDXL_FACE_LORA_FIXED

training_params = {**MINIMAL_DEFAULT_CONFIG, **SDXL_FACE_LORA_FIXED}

# 方法2: 既存のTrainingタブのsettings_list構築ロジックを再利用
# lora_gui.pyのsettings_list構築部分を関数化して再利用
```

**SDXL顔LoRA用プリセット** (`minimal/presets.py`):

```python
MINIMAL_DEFAULT_CONFIG = {
    'learning_rate': 0.0001,        # U-Net学習率
    'text_encoder_lr': 0.00005,     # Text Encoder学習率
    'network_dim': 16,             # LoRA rank（顔専用最適値）
    'network_alpha': 16,            # LoRA alpha
    'max_resolution': '512,512',   # 顔LoRA推奨解像度
    'train_batch_size': 1,          # メモリ効率重視
    'epoch': 6,                    # 適切なエポック数
    'max_train_steps': 1600,        # 最大ステップ数
    'cache_latents': True,         # 高速化
    'cache_latents_to_disk': True, # VRAM節約
    'save_model_as': 'safetensors',
    'save_precision': 'fp16',
    # ... 残り227個のパラメータ（デフォルト値）
}

SDXL_FACE_LORA_FIXED = {
    'sdxl': True,                  # SDXL有効
    'v2': False,                   # SD2.x無効
    'v_parameterization': False,   # 標準パラメータ化
    'flux1_checkbox': False,       # Flux無効
    # ... その他の固定パラメータ
}
```

#### ステップ4: Minimalパラメータマージ

- Trainingパラメータ（243個、辞書形式）に、Minimalパラメータ（16個、辞書形式）を上書き
- `final_params = {**training_params, **minimal_params}` の形式
- Minimalタブで設定した値が優先される
- マージ後のパラメータセット（243個）が完成

```python
# Trainingパラメータ（243個）にMinimalパラメータ（16個）を上書き
final_params = {**training_params, **minimal_params}
```

#### ステップ5: settings_list の構築

- マージ後のパラメータセットから、Trainingタブと同じ順序で `settings_list` を構築
- `kohya_gui/lora_gui.py` 2800行目以降の `settings_list` 構築ロジックを関数化して再利用
- `settings_list` の順序は、Trainingタブの `settings_list` 構築ロジックと同じ順序を維持

```python
# settings_list構築関数（lora_gui.pyの2800行目以降のロジックを関数化）
def build_settings_list(params: dict) -> list:
    """
    Trainingタブと同じ順序でsettings_listを構築
    
    Args:
        params: マージ後のパラメータ辞書（243個）
        
    Returns:
        list: train_model関数に渡すsettings_list（243個）
    """
    # lora_gui.py 2800行目以降のsettings_list構築ロジックと同じ順序
    return [
        params['pretrained_model_name_or_path'],
        params['v2'],
        params['v_parameterization'],
        params['sdxl'],
        params['flux1_checkbox'],
        params['dataset_config'],
        params['save_model_as'],
        params['save_precision'],
        params['train_data_dir'],
        params['output_name'],
        # ... 243個のパラメータを順序通りに
    ]

settings_list = build_settings_list(final_params)
```

#### ステップ6: トレーニング開始

- 既存の `train_model` 関数を、Trainingタブと同じ方法で呼び出す
- `train_model(headless, print_only, *settings_list)` の形式
- 以降の処理（バリデーション、コマンド構築、プロセス起動）は、Trainingタブと同じフロー

```python
from kohya_gui.lora_gui import train_model

result = train_model(
    headless=self.headless,
    print_only=False,
    *settings_list
)
```

### 5.4 処理フローの比較

#### Trainingタブの処理フロー

```
Trainingタブの「Start Training」押下
    ↓
settings_list（243個のパラメータ）が既に構築済み
    ↓
train_model(headless, print_only, *settings_list) を呼び出し
    ↓
train_model関数内で：
  - バリデーション処理
  - 設定の計算と準備
  - コマンドの構築
  - プロセス起動
```

#### Minimalタブの処理フロー（実装要件）

```
Minimalタブの「Start Training」押下
    ↓
Minimalパラメータ生成（16個）
    ↓
Trainingパラメータ生成（243個、デフォルト値）
    ↓
Minimalパラメータマージ（TrainingパラメータにMinimalパラメータを上書き）
    ↓
settings_list を構築（Trainingタブと同じ順序）
    ↓
train_model(headless, print_only, *settings_list) を呼び出し
    ↓
train_model関数内で：
  - バリデーション処理（Trainingタブと同じ）
  - 設定の計算と準備（Trainingタブと同じ）
  - コマンドの構築（Trainingタブと同じ）
  - プロセス起動（Trainingタブと同じ）
```

### 5.5 実装例（概念）

```python
def start_training(self, *minimal_args):
    """学習開始 - 既存のTrainingタブと同じパターン"""
    try:
        # 1. UI入力値の検証
        if not minimal_args[0]:  # pretrained_model_name_or_path
            return "エラー: チェックポイントパスが必要です"
        if not minimal_args[1] or not os.path.exists(minimal_args[1]):  # train_data_dir
            return "エラー: 有効な画像フォルダが必要です"
        # ... その他のバリデーション
        
        # 2. Minimalパラメータ生成（16個）
        minimal_params = {
            'pretrained_model_name_or_path': minimal_args[0],
            'train_data_dir': minimal_args[1],
            'output_name': minimal_args[2],
            'output_dir': minimal_args[3],
            'learning_rate': float(minimal_args[4]),
            'text_encoder_lr': float(minimal_args[5]),
            'network_dim': int(minimal_args[6]),
            'network_alpha': int(minimal_args[7]),
            'epoch': int(minimal_args[8]),
            'max_train_steps': int(minimal_args[9]),
            'max_resolution': minimal_args[10],
            'train_batch_size': int(minimal_args[11]),
            'cache_latents': bool(minimal_args[12]),
            'cache_latents_to_disk': bool(minimal_args[13]),
            'save_model_as': minimal_args[14],
            'save_precision': minimal_args[15],
        }
        
        # 3. Trainingパラメータ生成（243個、デフォルト値）
        from minimal.presets import MINIMAL_DEFAULT_CONFIG, SDXL_FACE_LORA_FIXED
        training_params = generate_training_defaults()  # 全243個のデフォルト値生成
        
        # 4. Minimalパラメータマージ
        final_params = {**training_params, **minimal_params}
        
        # 5. settings_list を構築（Trainingタブと同じ順序）
        settings_list = build_settings_list(final_params)
        
        # 6. train_model() 関数を既存と同じ方法で呼び出す
        from kohya_gui.lora_gui import train_model
        result = train_model(
            headless=self.headless,
            print_only=False,
            *settings_list
        )
        
        return result
    except Exception as e:
        return f"エラー: {str(e)}"
```

### 5.6 実装上の注意事項

- **UIコンポーネントの構築**: Minimalタブでは、UIコンポーネントを全て構築する必要はない（パラメータ値のみを扱う）
- **デフォルト値の生成**: Trainingパラメータの生成は、既存のTrainingタブの実装パターンを再利用
- **settings_list の構築**: `settings_list` の構築は、既存の `lora_gui.py` のロジックを関数化して再利用
- **順序の維持**: `settings_list` の順序は、Trainingタブの `settings_list` 構築ロジック（2800行目以降）と同じ順序を維持する必要がある

## 6. 設定ファイル管理

### 6.1 config.toml 自動保存システム

**リアルタイム保存メカニズム**:
- UI要素変更 → 即座に `auto_save_config()` が実行される
- オートセーブ時: `"✓ Auto-saved"` 表示
- 明示的保存時: `"設定をconfig.tomlに保存しました"` 表示
- エラー時: 具体的なエラーメッセージ表示

**Save Configボタン**:
- 常時有効（interactive=true）
- 明示的保存時に使用可能
- 自動保存とは独立して動作

### 6.2 config.toml 構造

```toml
# SDXL Face LoRA Minimal Configuration
# SDXL顔LoRA学習用のユーザー設定
# このファイルを編集して、UIの初期値をカスタマイズできます

[model]
pretrained_model_name_or_path = ""
save_model_as = "safetensors"
save_precision = "fp16"

[training_data]
train_data_dir = ""
max_resolution = "512,512"
train_batch_size = 1

[training_params]
learning_rate = 0.0001
text_encoder_lr = 0.00005
network_dim = 16
network_alpha = 16
epoch = 6
max_train_steps = 1600
cache_latents = true
cache_latents_to_disk = true

[output]
output_name = ""
output_dir = "./outputs"
```

## 7. SDXL顔LoRA最適化プリセット

### 7.1 プリセット値（`minimal/presets.py`）

```python
MINIMAL_DEFAULT_CONFIG = {
    # 学習率設定（顔LoRA専用チューニング）
    'learning_rate': 0.0001,        # U-Net: 1e-4（安定学習）
    'text_encoder_lr': 0.00005,     # TextEnc: 5e-5（過学習防止）
    
    # LoRA設定（顔特徴最適化）
    'network_dim': 16,              # Rank 16（品質/サイズバランス）
    'network_alpha': 16,            # Alpha 16（学習安定性）
    
    # データ設定
    'max_resolution': '512,512',    # 顔LoRA標準解像度
    'train_batch_size': 1,          # メモリ効率重視
    
    # 学習制御
    'epoch': 6,                     # 適切な学習回数
    'max_train_steps': 1600,        # 過学習防止
    
    # 最適化設定
    'cache_latents': True,          # 高速化有効
    'cache_latents_to_disk': True,  # VRAM節約有効
    
    # 出力設定
    'save_model_as': 'safetensors', # 標準フォーマット
    'save_precision': 'fp16',       # 混合精度（効率性）
    
    # ... 残り227個のパラメータ（デフォルト値）
}

SDXL_FACE_LORA_FIXED = {
    'sdxl': True,                   # SDXL専用フラグ
    'v2': False,                    # SD2.x無効
    'v_parameterization': False,    # 標準パラメータ化
    'flux1_checkbox': False,        # Flux無効
    # ... その他の固定パラメータ
}
```

### 7.2 選択肢設定

```python
RESOLUTION_CHOICES = [
    '512,512',    # 顔LoRA推奨
    '768,768',    # 高解像度顔
    '1024,1024'   # 最高解像度（要メモリ）
]

BATCH_SIZE_CHOICES = [1, 2, 4]           # メモリ容量に応じて
SAVE_MODEL_AS_CHOICES = ['safetensors', 'ckpt']  # 標準フォーマット
SAVE_PRECISION_CHOICES = ['fp16', 'bf16', 'float']  # 精度選択
```

## 8. コア実装詳細

### 8.1 メインタブクラス (sdxl_simple_tab.py)

```python
class SDXLSimpleTab:
    """SDXL顔LoRA専用簡易UIタブ"""
    
    def __init__(self, headless: bool = False, config: Any = None, use_shell_flag: bool = False):
        """初期化"""
        self.headless = headless
        self.config = config
        self.use_shell_flag = use_shell_flag
        self.config_path = Path(__file__).parent / "config.toml"
        
    def create_ui(self) -> None:
        """Gradio UI構築"""
        # UI要素作成 + イベントハンドラ設定
        # 自動保存イベント追加
        
    def auto_save_config(self, *args) -> str:
        """値変更時自動保存"""
        # リアルタイム保存処理
        
    def save_config(self, *args) -> str:
        """設定をconfig.tomlに保存"""
        # TOML形式での永続化
        
    def start_training(self, *args) -> str:
        """学習開始（最新設計思想に基づく実装）"""
        # 1. Minimalパラメータ生成（16個）
        # 2. Trainingタブのデフォルト値を取得（UIコンポーネントの初期値、生成しない）
        # 3. Minimalパラメータマージ
        # 4. settings_list 構築（train_model関数の引数順序と完全に一致）
        # 5. train_model() 呼び出し
        
    def _generate_minimal_params(self, *ui_args) -> dict:
        """Minimalパラメータ生成（16個）"""
        # UI入力値から16個のパラメータを辞書形式で生成
        
    def _get_training_defaults(self) -> dict:
        """Trainingタブのデフォルト値を取得（UIコンポーネントの初期値、生成しない）"""
        # TrainingタブのUIコンポーネントの初期値をハードコード
        # SDXL顔LoRA用の最適化済みデフォルト値を適用
        
    def _generate_minimal_params(self, *ui_args) -> dict:
        """Minimalパラメータ生成（16個）"""
        # UI入力値から16個のパラメータを辞書形式で生成
        
    def _merge_params(self, training_defaults: dict, minimal_params: dict) -> dict:
        """Minimalパラメータマージ"""
        # Trainingタブのデフォルト値にMinimalパラメータを上書き
        # text_encoder_lrとlearning_rateが異なる場合、down_lr_weightとup_lr_weightを設定
        
    def _build_settings_list(self, params: dict) -> list:
        """settings_list を構築（train_model関数の引数順序と完全に一致）"""
        # minimal/utils.py の build_settings_list_from_params() を呼び出し
        # inspect.signature を使用して train_model 関数の引数順序を取得
        
    def _get_all_inputs(self) -> List[gr.Component]:
        """全UI要素のリスト取得"""
        # イベントバインディング用
    
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
        # 1. 入力検証（キャプションテキスト、フォルダパスの存在確認）
        # 2. 既存キャプションファイルの確認（上書き確認）
        # 3. kohya_gui.basic_caption_gui.caption_images() を呼び出し
        # 4. 生成結果の表示（画像ファイル数、キャプションファイル数）
```

### 8.2 Caption生成機能の実装詳細

#### 8.2.1 UIコンポーネント

**実装場所**: `minimal/sdxl_simple_tab.py` 127-155行目

```python
# Caption Generation Accordion
with gr.Accordion("Caption Generation", open=False):
    gr.Markdown("**固定キャプションを全画像に一括生成** - 学習前の事故を防ぐための補助機能")
    gr.Markdown("*画像フォルダ（Image folder）に指定されたフォルダに自動的にキャプションを生成します*")
    
    # Caption text
    self.caption_text = gr.Textbox(
        label="Caption text",
        placeholder="例: character_name, face, portrait",
        value=MINIMAL_USER_CONFIG.get('caption_text', ''),
        info="全画像に適用する固定キャプションテキスト",
        lines=2
    )
    
    # Overwrite checkbox
    self.caption_overwrite = gr.Checkbox(
        label="Overwrite existing captions",
        value=False,
        info="既存の.txtファイルがある場合に上書きする（⚠️ 注意: 既存キャプションが失われます）"
    )
    
    # Generate button & Result display
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
```

**注意**: Caption folderのUIコンポーネントは削除され、`train_data_dir`（Image folder）が自動的に使用されます。

#### 8.2.2 イベントハンドラ

**実装場所**: `minimal/sdxl_simple_tab.py` 360-370行目

```python
# キャプション生成ボタン
self.generate_captions_button.click(
    fn=self.generate_captions,
    inputs=[
        self.caption_text,
        self.train_data_dir,  # Image folderを自動使用
        self.caption_overwrite
    ],
    outputs=[self.caption_result],
    show_progress=True
)
```

#### 8.2.3 generate_captions() メソッドの実装

**実装場所**: `minimal/sdxl_simple_tab.py` 410-487行目

**処理フロー**:
1. **入力検証**
   - キャプションテキストが空でないことを確認
   - `train_data_dir`（Image folder）が指定されていることを確認
   - フォルダが存在することを確認
   - パスがディレクトリであることを確認

2. **サブフォルダの自動検出（kohya_ssの仕様に準拠）**
   - `train_data_dir`の下にあるサブフォルダを検索
   - サブフォルダが0個の場合: エラーメッセージを返す
   - サブフォルダが複数ある場合: エラーメッセージを返す（今回は1つのサブフォルダのみサポート）
   - サブフォルダが1個の場合: そのサブフォルダを実際の画像フォルダとして使用
   - 例: `training_data/5_SATOMI` が実際に使用されるフォルダ

3. **既存キャプションファイルの確認**
   - `overwrite=False` の場合、既存の`.txt`ファイルを検索
   - 既存ファイルがある場合は警告メッセージを返す

4. **caption_images() 関数の呼び出し**
   - `kohya_gui.basic_caption_gui.caption_images()` をインポート
   - 以下のパラメータで呼び出し:
     - `caption_text`: 固定キャプションテキスト
     - `images_dir`: 画像フォルダパス
     - `overwrite`: 上書きフラグ
     - `caption_ext`: ".txt"
     - `prefix`, `postfix`, `find_text`, `replace_text`: 空文字列（固定キャプション生成のため）

5. **生成結果の表示**
   - 画像ファイル数をカウント（Jpeg系のみ: `.jpg`, `.jpeg`, `.png`, `.webp`, `.bmp`）
   - キャプションファイル数をカウント（`.txt`のみ）
   - `os.listdir`でファイルを列挙し、拡張子で正確にフィルタリング
   - 大文字小文字の違いも考慮（`.JPG`と`.jpg`の両方を認識）
   - 結果メッセージを返す（「画像ファイル（Jpeg系）: X個」「キャプションファイル（.txt）: X個」）

**kohya_ssのフォルダ構造仕様**:
- `train_data_dir`（例: `training_data/`）は親フォルダ
- その下にサブフォルダ（例: `5_SATOMI`）が1個存在する
- 実際の画像はサブフォルダ内に配置される
- Caption生成は、このサブフォルダに対して実行される

**エラーハンドリング**:
- すべてのエラーをキャッチし、エラーメッセージを返す
- ログにエラー情報を記録

#### 8.2.4 仕様要件との対応

**Specification_001.md ⑥ Caption一括生成（重要）の要件**:
- ✅ 固定 caption を全画像に一括生成
- ✅ 既存 `.txt` がある場合は必ず上書き確認（`overwrite=False`の場合に警告表示）
- ✅ 学習前の事故を防ぐための補助機能

### 8.3 実装のポイント

- **UIコンポーネントを構築する必要はない**: パラメータ値のみを扱う
- **デフォルト値の生成**: 既存のTrainingタブの実装パターンを再利用
- **Minimalタブの変更は最小限**: 16個の値の上書きのみ
- **settings_list の構築**: 既存の `lora_gui.py` のロジックを関数化して再利用

## 9. 意図的に実装しない項目

以下は **設計判断としてUIに出さない**：

* optimizer / lr scheduler の変更
* network_module / network_args の詳細設定
* 正則化画像（reg images）
* 複数 dataset / subset
* フォルダ名 repeat 方式

**理由**:
* 操作ミスが増える
* 本タブの目的（再現性・安定性）から外れる
* ここを触り始めると「研究モード」に入る

## 10. 切り捨て・無効化ポリシー

* `minimal/` ディレクトリ削除で完全無効化
* kohya-ss 本体に影響なし
* `lora_gui.py` の8行削除で元に戻る
* upstream 更新時の衝突は最小

## 11. 関連ドキュメント

- **基本仕様**: [Specification_001.md](Specification_001.md)
- **設計要件**: [Design_Requirement_001.md](Design_Requirement_001.md)
- **実装アプローチ**: [AlternativeApproach.md](AlternativeApproach.md)
- **Trainingタブの挙動調査**: [investigation/lora_start_training_flow.md](investigation/lora_start_training_flow.md)
- **settings_list の構築**: `kohya_gui/lora_gui.py` 2800行目以降

## 12. まとめ（実装者向け）

> このMinimalタブは
> **「SDXL顔LoRAを、毎回同じ考え方・同じ品質で作るために、
> 本当に必要なパラメータだけを安全に操作できる補助UI」**
> です。
>
> **学習の仕組みは変えていません。**
> **変えたのは「操作の迷い」と「事故の起きやすさ」だけです。**
>
> **Minimalタブの「Start Training」ボタンは、Trainingタブの挙動を模倣し、**
> **既存の実装パターンを最大限活用することで、保守性と一貫性を確保します。**

---

**最終更新**: 2026-01-11  
**バージョン**: FULL (統合版)  
**設計思想**: 「最低限のUIでTrainingを開始する」 + 「Trainingタブの挙動を模倣する」
