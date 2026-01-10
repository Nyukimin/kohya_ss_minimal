# SDXL専用 LoRA簡易タブ

## 実装仕様書（修正版 v2.0）

---

## 1. 目的と設計思想（重要）

本仕様は、`kohya_ss` に **SDXL顔LoRA作成に特化した簡易UI**を追加するための実装指針を定める。

### 1.1 基本設計思想

**MinimalはUIレイヤーのみ。処理ロジックは既存機能をそのまま利用。**

- **UI専用**: パラメータ入力画面のみを提供
- **既存機能活用**: kohya-ss の既存処理系を直接呼び出し
- **処理重複なし**: caption生成、dataset設定、学習実行は既存関数を使用
- **最小修正**: Fork元への変更は1つのタブ追加のみ

### 1.2 Minimalの役割

> **Minimal = 「既存LoRAタブの簡易版UI」**
> 
> 標準LoRAタブと**全く同じ処理**を、**簡潔なUIで操作**するためのインターフェース

---

## 2. ディレクトリ構成（正しい構成）

### 2.1 Fork元への修正（最小限）

```text
kohya_gui/lora_gui.py    # LoRAタブ内にMinimalサブタブ追加（8行のみ）
```

### 2.2 Minimal実装ディレクトリ

```text
minimal/
├── __init__.py                          # Python package
├── sdxl_simple_tab.py                   # UI定義 + 既存関数呼び出し
├── presets.py                           # SDXL顔LoRA用デフォルト値
├── config.toml                          # 推奨設定値（参考用）
├── README.md                            # プロジェクト説明
└── docs/
   ├── Specification_001.md              # 基本仕様（変更なし）
   └── ImplementationSpecification_002.md # 本ファイル（修正版）
```

---

## 3. 実装方針（重要）

### 3.1 既存機能の活用

#### **NG**: 独自実装
- ❌ caption生成ロジックの実装
- ❌ dataset_config.toml生成の実装
- ❌ 学習プロセス実行の実装
- ❌ 新しい学習方式の開発

#### **OK**: 既存関数呼び出し
- ✅ `kohya_gui/lora_gui.py` の `train_model()` 関数
- ✅ 既存のcaption生成機能
- ✅ 既存のdataset設定機能
- ✅ 既存のファイル選択機能

### 3.2 UI仕様

#### **Accordion構成**（既存UIパターンに合わせる）

```python
with gr.Tab("Minimal"):
    with gr.Accordion("Model Source", open=True):
        # checkpoint選択、保存設定
    with gr.Accordion("Training Data", open=True):
        # 画像フォルダ、repeat、解像度
    with gr.Accordion("Training Parameters", open=True):
        # 学習率、LoRA設定、バッチ設定
    with gr.Accordion("Caption", open=True):
        # 既存caption機能のUI呼び出し
    with gr.Accordion("Output", open=True):
        # 出力設定
    with gr.Accordion("Training", open=True):
        # 学習実行ボタン + ログ表示
```

---

## 4. 実装ファイル詳細

### 4.1 `sdxl_simple_tab.py`

#### **役割**: UI定義のみ

```python
class SDXLSimpleTab:
    def __init__(self, headless, config, use_shell_flag):
        # 既存LoRAタブと同じ初期化
        
    def create_ui(self):
        # Accordion形式のUI定義
        # config.tomlからデフォルト値設定
        
    def start_training(self, *args):
        # 既存のtrain_model()関数を呼び出し
        from kohya_gui.lora_gui import train_model
        return train_model(*converted_args)
        
    def generate_captions(self, folder, caption):
        # 既存のcaption生成機能を呼び出し
        # UIパラメータを既存関数の引数に変換
```

#### **重要**: 新しい処理は一切実装しない

### 4.2 `presets.py`

#### **役割**: SDXL顔LoRA用デフォルト値

```python
SDXL_FACE_LORA_DEFAULTS = {
    'learning_rate': '1e-4',
    'text_encoder_lr': '5e-5',
    'network_dim': 16,
    'network_alpha': 16,
    'max_resolution': '512,512',
    'max_train_steps': 1600,
    'batch_size': 1,
    'cache_latents': True,
    'cache_latents_to_disk': True,
    'save_model_as': 'safetensors',
    'save_precision': 'fp16',
    'mixed_precision': 'fp16'
}
```

---

## 5. 実装手順

### 5.1 段階的実装

1. **UI作成**: Accordion形式でパラメータ入力画面
2. **プリセット適用**: config.tomlの値をデフォルトに設定
3. **既存関数連携**: UIの値を既存関数の引数形式に変換
4. **動作確認**: 標準LoRAタブと同じ結果が出ることを確認

### 5.2 データフロー

```
[Minimal UI] → [パラメータ変換] → [既存train_model()] → [学習実行]
     ↓              ↓                    ↓
[簡易入力]    [標準形式変換]        [既存処理]
```

---

## 6. 意図的に実装しない項目（重要）

以下は**設計判断として実装しない**：

### 6.1 独自処理系
- 新しいcaption生成ロジック
- 新しいdataset設定ロジック  
- 新しい学習実行ロジック
- 新しい保存・読み込み機能

### 6.2 複雑なUI機能
- 高度なパラメータ設定
- 複数dataset/subset
- カスタムoptimizer/scheduler
- 正則化画像設定

**理由**: 本タブは「簡易化」が目的。高度な機能は標準LoRAタブを使用。

---

## 7. テスト方針

### 7.1 同等性テスト

**Minimalタブ = 標準LoRAタブ**の動作確認：

1. 同じパラメータでMinimalと標準の両方で学習
2. 出力モデルが同一であることを確認  
3. ログ出力が同一であることを確認

### 7.2 UI機能テスト

- パラメータ入力の妥当性確認
- エラーハンドリングの動作確認
- 既存機能との干渉がないことを確認

---

## 8. 切り捨て・無効化ポリシー

- `minimal/` ディレクトリ削除で完全無効化
- kohya-ss 本体への影響なし
- lora_gui.pyの8行削除で元に戻る

---

## 9. 一文まとめ（修正版）

> このMinimalタブは
> **「既存のLoRA学習機能をそのまま使い、
> SDXL顔LoRA用の最小限UIでアクセスできる簡易インターフェース」**
> である。
>
> 新しい処理は一切実装せず、UI（見た目）だけを変える。

---

## 10. 変更履歴

- **v1.0** (ImplementationSpecification_001.md): 独自処理系実装（❌誤った設計）
- **v2.0** (本ファイル): UI専用、既存機能活用（✅正しい設計）

---

**最終更新**: 2026-01-10  
**バージョン**: 2.0  
**担当**: Claude Code AI Assistant