# SDXL Face LoRA Minimal Tab Implementation Specification (002)
**Version:** 2.0  
**Date:** 2026-01-11  
**Status:** 実装完了 + テスト完了

## 概要

SDXL顔LoRA学習用の最小限UIタブを既存のkohya_ssに追加。既存機能を活用しつつ、初心者向けの簡易インターフェースを提供。

## 実装アーキテクチャ

### 基本方針
- **UI専用レイヤー**: 既存のtrain_model()関数を呼び出すのみ
- **最小限変更**: 本体への修正は8行のみ（lora_gui.pyにMinimalタブ追加）
- **独立性**: minimal/フォルダに全コードを分離
- **設定自動保存**: UI値変更時に自動でconfig.toml更新

### ファイル構成

```
kohya_ss_minimal/
├── kohya_gui/
│   └── lora_gui.py          # [修正] Minimalタブを追加（8行）
└── minimal/                 # [新規] 全機能をここに実装
    ├── __init__.py
    ├── config.toml          # ユーザー設定ファイル（自動更新）
    ├── presets.py           # SDXL顔LoRA最適化プリセット
    ├── sdxl_simple_tab.py   # メインUI実装
    ├── docs/                # ドキュメント
    │   ├── ImplementationSpecification_001.md
    │   ├── ImplementationSpecification_002.md  # ←このファイル
    │   └── README.md
    └── tests/               # TDDテストスイート
        ├── __init__.py
        ├── run_tests.py     # テスト実行スクリプト
        ├── test_config.py   # config.toml関連テスト
        ├── test_presets.py  # プリセット値テスト
        └── test_sdxl_simple_tab.py  # メインタブ機能テスト
```

## 主要機能

### 1. UI構成

```
LoRA Tab
├── Training
├── Tools 
├── Guides
└── Minimal              # ←新規追加
    ├── Model Source     # SDXLチェックポイント、保存設定
    ├── Training Data    # 画像フォルダ、解像度、バッチサイズ
    ├── Training Params  # 学習率、LoRA設定、エポック
    ├── Output Settings  # 出力名、出力フォルダ
    └── Training         # 学習開始/停止、ログ表示
```

### 2. 自動保存システム

**リアルタイム保存**:
- UI要素の値変更 → 即座にconfig.tomlに保存
- オートセーブ時: "✓ Auto-saved"表示
- 明示的保存時: "設定をconfig.tomlに保存しました"表示
- エラー時: 具体的なエラーメッセージ表示

**Save Configボタン**:
- 常時有効（interactive=true）
- 明示的保存時に使用可能
- 自動保存とは独立して動作

### 3. SDXL顔LoRA最適化プリセット

```python
SDXL_FACE_LORA_DEFAULTS = {
    'learning_rate': 0.0001,      # U-Net学習率
    'text_encoder_lr': 0.00005,   # Text Encoder学習率
    'network_dim': 16,            # LoRA rank（顔専用最適値）
    'network_alpha': 16,          # LoRA alpha
    'max_resolution': '512,512',  # 顔LoRA推奨解像度
    'train_batch_size': 1,        # メモリ効率重視
    'epoch': 6,                   # 適切なエポック数
    'max_train_steps': 1600,      # 最大ステップ数
    'cache_latents': True,        # 高速化
    'cache_latents_to_disk': True,# VRAM節約
    'save_model_as': 'safetensors',
    'save_precision': 'fp16'
}

SDXL_FACE_LORA_FIXED = {
    'sdxl': True,                 # SDXL有効
    'v2': False,                  # SD2.x無効
    'v_parameterization': False,  # 標準パラメータ化
    'flux1_checkbox': False       # Flux無効
}
```

## コア実装

### 1. メインタブ実装 (sdxl_simple_tab.py)

**クラス構造**:
```python
class SDXLSimpleTab:
    def __init__(self, headless, config, use_shell_flag)
    def create_ui(self)                    # GradioUI作成
    def save_config(self, *args)           # config.toml保存
    def auto_save_config(self, *args)      # 自動保存処理
    def start_training(self, *args)        # 学習開始
    def _convert_ui_to_train_args(self, *args)  # UI→train_model引数変換
    def _get_all_inputs(self)              # UI要素リスト取得
```

**重要な処理フロー**:
1. UI値変更 → `auto_save_config()` → `save_config(*args)` → config.toml更新
2. 学習開始 → `start_training()` → バリデーション → `train_model()`呼び出し
3. 設定保存 → `save_config()` → TOML形式でファイル出力

### 2. 本体統合 (lora_gui.py)

```python
# kohya_gui/lora_gui.py に追加（8行のみ）
with gr.Tab("Minimal"):
    try:
        from minimal.sdxl_simple_tab import sdxl_simple_tab
        sdxl_simple_tab(headless=headless, config=config, use_shell_flag=use_shell)
    except ImportError:
        gr.Markdown("**SDXL Simple tab not available**")
```

### 3. 設定ファイル構造 (config.toml)

```toml
# SDXL Face LoRA Minimal Configuration
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

## テスト実装

### TDDテストスイート (23テスト)

**実行コマンド**:
```bash
python minimal/tests/run_tests.py
```

**テスト結果**: ✅ 全23テスト合格

## 結論

SDXL顔LoRA学習用の最小限UIタブが完全に実装され、自動保存機能により使いやすさが大幅に向上しました。