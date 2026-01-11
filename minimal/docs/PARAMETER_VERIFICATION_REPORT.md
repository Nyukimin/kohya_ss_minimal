# パラメータ形式検証レポート

**日付**: 2026-01-11  
**対象**: `minimal/sdxl_simple_tab.py` の `_convert_ui_to_train_args` メソッド

## 検証結果サマリー

### ✅ 正しい点

1. **`max_resolution`の形式**: 文字列 `'512,512'` で正しい
   - kohya-ssの期待形式と一致（`gr.Textbox`で定義）
   - `train_model`関数内で`"resolution": max_resolution`として使用される

2. **`max_resolution`の位置**: 位置17（0-based index）で正しく配置されている
   - `train_model`関数の期待位置と一致

3. **パラメータの型**: 各パラメータは適切な型で配置されている
   - 文字列、整数、浮動小数点数、ブール値が正しく設定されている

### ❌ 重大な問題

**引数の数が不足しています**

- **`_convert_ui_to_train_args`が返す引数**: 115個
- **`train_model`関数が期待する引数**: 231個
- **不足している引数**: 116個（位置115以降）

#### 不足している引数の例（位置115以降）

```
115: debiased_estimation_loss
116: sdxl_cache_text_encoder_outputs
117: sdxl_no_half_vae
118: text_encoder_lr          ← UIから取得しているが、引数リストに含まれていない
119: t5xxl_lr
120: unet_lr
121: network_dim              ← UIから取得しているが、引数リストに含まれていない
122: network_weights
123: dim_from_weights
124: network_alpha             ← UIから取得しているが、引数リストに含まれていない
125: LoRA_type
126: factor
127: bypass_mode
... (以下、残り約100個)
```

## 仕様との整合性

### Specification_001.md の要求事項

1. ✅ **ベースモデル（Checkpoint）の切り替え**: 実装済み
2. ✅ **学習データ指定**: 実装済み
3. ❌ **Repeat（num_repeats）の明示指定**: 未実装（`ImplementationSpecification_004.md`でギャップとして記載）
4. ✅ **学習量の制御**: 実装済み
5. ✅ **主要学習パラメータ**: 実装済み（ただし、引数リストに含まれていない）
6. ❌ **Caption一括生成**: 未実装（`ImplementationSpecification_004.md`でギャップとして記載）

### ImplementationSpecification_004.md の現状

- **現状実装**: 115個の引数を返している
- **ギャップ**: Caption一括生成、Repeat/dataset_config生成が未実装
- **技術スタック**: Python 3.10-3.12（`pyproject.toml`準拠）

## 推奨対応

### 緊急対応（必須）

`_convert_ui_to_train_args`メソッドを修正し、`train_model`関数が期待する全231個の引数を返すようにする必要があります。

特に重要な不足引数：
- `debiased_estimation_loss` (115)
- `sdxl_cache_text_encoder_outputs` (116)
- `sdxl_no_half_vae` (117)
- `text_encoder_lr` (118) - UIから取得済みだが引数リストに含まれていない
- `t5xxl_lr` (119)
- `unet_lr` (120)
- `network_dim` (121) - UIから取得済みだが引数リストに含まれていない
- `network_weights` (122)
- `dim_from_weights` (123)
- `network_alpha` (124) - UIから取得済みだが引数リストに含まれていない
- `LoRA_type` (125)
- ... (残り約100個)

### 実装方針

1. `train_model`関数の全引数を確認
2. `presets.py`に不足しているデフォルト値を追加
3. `_convert_ui_to_train_args`メソッドを修正して全231個の引数を返すようにする

## 参考情報

- **プロジェクト仕様**: `minimal/docs/Specification_001.md`
- **実装仕様**: `minimal/docs/ImplementationSpecification_004.md`
- **設計思想**: `minimal/README.md`
- **kohya-ss本体**: `README.md`
