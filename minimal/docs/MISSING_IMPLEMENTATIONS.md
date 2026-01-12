# 不足している実装一覧

## 概要

`ImplementationSpecification_Design_Requirement_001_VERIFIED.md`で定義された実装仕様に基づき、現在の実装状況を確認した結果、以下の実装が不足しています。

## 不足している実装

### 1. `minimal/utils.py` モジュール（新規作成が必要）

**関数**: `build_settings_list_from_params()`

**説明**: `train_model`関数の引数順序（`headless`と`print_only`を除く）と同じ順序で`settings_list`を構築する関数

**実装要件**:
- `inspect.signature`を使用して`train_model`関数の引数順序を取得
- その順序に従ってパラメータ辞書から値を取得してリストを構築
- **最重要**: 順序は`train_model`関数の引数順序と完全に一致している必要がある

**現在の状態**: ❌ 未実装（`minimal/utils.py`ファイル自体が存在しない）

---

### 2. `minimal/sdxl_simple_tab.py` の`SDXLSimpleTab`クラス

#### 2.1. `_get_training_defaults()` メソッド

**説明**: TrainingタブのUIコンポーネントの初期値（デフォルト値）を取得するメソッド

**実装要件**:
- TrainingタブのUIコンポーネントの初期値をハードコード
- SDXL顔LoRA用の最適化済みデフォルト値を適用（`MINIMAL_DEFAULT_CONFIG`、`SDXL_FACE_LORA_FIXED`）
- 229個のパラメータのデフォルト値を含む辞書を返す

**現在の状態**: ❌ 未実装

---

#### 2.2. `_generate_minimal_params()` メソッド

**説明**: MinimalタブのUI入力値から、16個のパラメータを辞書形式で生成するメソッド

**実装要件**:
- MinimalタブのUI入力値（16個）を受け取る
- パラメータ名と値のマッピングを行い、辞書形式で返す
- 型変換（`float`、`int`、`bool`）を適切に行う

**現在の状態**: ❌ 未実装

---

#### 2.3. `_merge_params()` メソッド

**説明**: Trainingタブのデフォルト値に、Minimalタブで設定した値を上書きするメソッド

**実装要件**:
- Trainingタブのデフォルト値辞書（229個）とMinimalタブのパラメータ辞書（16個）を受け取る
- Minimalタブの値でTrainingタブのデフォルト値を上書き
- マージ後のパラメータ辞書（229個）を返す

**現在の状態**: ❌ 未実装

---

#### 2.4. `_build_settings_list()` メソッド

**説明**: マージ後のパラメータ辞書から、`train_model`関数の引数順序と同じ順序で`settings_list`を構築するメソッド

**実装要件**:
- マージ後のパラメータ辞書（229個）を受け取る
- `minimal.utils.build_settings_list_from_params()` 関数を呼び出す
- `settings_list`（229個の実際の値）を返す

**現在の状態**: ❌ 未実装

---

#### 2.5. `start_training()` メソッドの更新

**説明**: 既存の`_convert_ui_to_train_args()`を使用した実装を、新しい実装フロー（5ステップ）に置き換える

**実装要件**:
1. Minimalパラメータ生成（16個） - `_generate_minimal_params()`を呼び出す
2. Trainingタブのデフォルト値を取得 - `_get_training_defaults()`を呼び出す
3. Minimalパラメータマージ - `_merge_params()`を呼び出す
4. `settings_list`を構築 - `_build_settings_list()`を呼び出す
5. `train_model()`関数を呼び出す - `headless`と`print_only`を除く引数として`settings_list`を渡す

**現在の状態**: ⚠️ 部分実装（`_convert_ui_to_train_args()`を使用した古い実装が残っている）

**注意**: 既存の`_convert_ui_to_train_args()`メソッドは、新しい実装フローに置き換える必要があるため、削除または非推奨にする必要がある。

---

## 実装チェックリスト

### 優先度: 最高（システム崩壊のリスク）

- [ ] **`minimal/utils.py` モジュールを作成**
  - [ ] `build_settings_list_from_params()` 関数を実装
  - [ ] `inspect.signature`を使用して`train_model`関数の引数順序を取得
  - [ ] その順序に従ってパラメータ辞書から値を取得してリストを構築
  - [ ] 順序の検証を実施

### 優先度: 高（新しい実装フローの基盤）

- [ ] **`_get_training_defaults()` メソッドを実装**
  - [ ] TrainingタブのUIコンポーネントの初期値をハードコード
  - [ ] SDXL顔LoRA用の最適化済みデフォルト値を適用
  - [ ] デフォルト値の検証を実施

- [ ] **`_generate_minimal_params()` メソッドを実装**
  - [ ] MinimalタブのUI入力値から16個のパラメータを辞書形式で生成
  - [ ] 型変換を適切に行う

- [ ] **`_merge_params()` メソッドを実装**
  - [ ] Trainingタブのデフォルト値に、Minimalタブの値を上書き

- [ ] **`_build_settings_list()` メソッドを実装**
  - [ ] マージ後のパラメータ辞書から、`train_model`関数の引数順序と同じ順序で`settings_list`を構築
  - [ ] `build_settings_list_from_params()` 関数を呼び出す

### 優先度: 中（既存実装の置き換え）

- [ ] **`start_training()` メソッドを更新**
  - [ ] 既存の`_convert_ui_to_train_args()`を使用した実装を削除
  - [ ] 新しい実装フロー（5ステップ）に置き換え
  - [ ] 入力検証は維持

- [ ] **`_convert_ui_to_train_args()` メソッドの処理**
  - [ ] 削除するか、非推奨としてマーク
  - [ ] 新しい実装フローに移行後、削除を検討

### 優先度: 低（テストと検証）

- [ ] **テスト**
  - [ ] `settings_list`の順序が`train_model`関数の引数順序と完全に一致していることを確認
  - [ ] `settings_list`の要素数が229個であることを確認
  - [ ] Minimalタブで設定した値が正しく反映されることを確認
  - [ ] Trainingタブと同じ結果が得られることを確認

---

## 現在の実装状況

### 実装済み

- ✅ `SDXLSimpleTab`クラスの基本構造
- ✅ UIコンポーネントの作成
- ✅ `start_training()`メソッドの基本構造（古い実装）
- ✅ `_convert_ui_to_train_args()`メソッド（古い実装、置き換えが必要）
- ✅ `save_config()`メソッド
- ✅ `auto_save_config()`メソッド

### 未実装

- ❌ `minimal/utils.py`モジュール
- ❌ `build_settings_list_from_params()`関数
- ❌ `_get_training_defaults()`メソッド
- ❌ `_generate_minimal_params()`メソッド
- ❌ `_merge_params()`メソッド
- ❌ `_build_settings_list()`メソッド
- ❌ `start_training()`メソッドの新しい実装フロー

---

## 実装の影響範囲

### システム的な崩壊のリスク

**最重要**: `build_settings_list_from_params()`関数の実装が不正確な場合、`train_model`関数に間違った引数が渡され、システム的な崩壊につながる可能性があります。

**対策**:
- `inspect.signature`を使用して`train_model`関数の引数順序を取得し、その順序に従って`settings_list`を構築する
- 順序の検証を実施する

### 既存機能への影響

- `start_training()`メソッドの更新により、既存の`_convert_ui_to_train_args()`メソッドは使用されなくなる
- 新しい実装フローは、Trainingタブの挙動を正確に模倣するため、より安全で信頼性が高い

---

## 関連ドキュメント

- **実装仕様**: [ImplementationSpecification_Design_Requirement_001_VERIFIED.md](ImplementationSpecification_Design_Requirement_001_VERIFIED.md)
- **設計要件**: [Design_Requirement_001.md](Design_Requirement_001.md)
