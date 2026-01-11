# 設計要件: Minimalタブの「Start Training」ボタンの挙動

## 要件定義

**Minimalタブの「Start Training」ボタンは、LoRAタブのTrainingタブの「Start Training」ボタンの挙動を模倣する。**

## Trainingタブの処理フロー（分解）

Trainingタブの「Start Training」から学習プロセス開始までの処理フローは、[investigation/lora_start_training_flow.md](investigation/lora_start_training_flow.md) に詳細が記載されています。

### Trainingタブの処理フロー概要

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

## Minimalタブの処理フロー（要件）

### 処理フローの分解

Minimalタブの「Start Training」ボタン押下時の処理フローは、以下の通りです：

1. **Minimalタブの「Start Training」押下**
   - MinimalタブのUIから16個のパラメータを取得

2. **Minimalパラメータ生成**
   - MinimalタブのUI入力値から、16個のパラメータを生成
   - 例: `pretrained_model_name_or_path`, `train_data_dir`, `output_name`, `output_dir`, `learning_rate`, `text_encoder_lr`, `network_dim`, `network_alpha`, `epoch`, `max_train_steps`, `max_resolution`, `train_batch_size`, `cache_latents`, `cache_latents_to_disk`, `save_model_as`, `save_precision`

3. **Trainingパラメータ生成**
   - 既存のTrainingタブと同じように、全243個のパラメータをデフォルト値で生成
   - Trainingタブの `settings_list` 構築ロジック（`lora_gui.py` 2800行目以降）と同じ方法で、デフォルト値を生成
   - この時点では、Trainingタブのデフォルト値が設定される

4. **Minimalパラメータマージ**
   - Trainingパラメータ（243個）に、Minimalパラメータ（16個）を上書き
   - Minimalタブで設定した値が優先される
   - マージ後のパラメータセット（243個）が完成

5. **settings_list の構築**
   - マージ後のパラメータセットから、Trainingタブと同じ順序で `settings_list` を構築
   - `lora_gui.py` 2800行目以降の `settings_list` 構築ロジックと同じ順序を維持

6. **トレーニング開始**
   - 既存の `train_model` 関数を、Trainingタブと同じ方法で呼び出す
   - `train_model(headless, print_only, *settings_list)` の形式
   - 以降の処理（バリデーション、コマンド構築、プロセス起動）は、Trainingタブと同じフロー

### 実装方針

1. **Minimalパラメータ生成**
   - MinimalタブのUI入力値から、16個のパラメータを辞書形式で生成

2. **Trainingパラメータ生成**
   - 既存のTrainingタブのデフォルト値生成ロジックを再利用
   - 全243個のパラメータをデフォルト値で生成（SDXL顔LoRA用の最適化済みデフォルト値）

3. **Minimalパラメータマージ**
   - Trainingパラメータ（辞書）に、Minimalパラメータ（辞書）を上書き
   - `final_params = {**training_params, **minimal_params}` の形式

4. **settings_list の構築**
   - マージ後のパラメータセットから、Trainingタブと同じ順序で `settings_list` を構築
   - `lora_gui.py` 2800行目以降の `settings_list` 構築ロジックを関数化して再利用

5. **train_model の呼び出し**
   - Trainingタブと同じ方法で `train_model` 関数を呼び出す
   - `train_model(headless, print_only, *settings_list)`

### 処理フローの比較

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

#### Minimalタブの処理フロー（要件）

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

### 利点

この実装パターンにより：

1. **一貫性**: Trainingタブと同じ実装パターンを使用することで、コードの一貫性が保たれる
2. **保守性**: `train_model` 関数のシグネチャが変更されても、自動的に対応される
3. **理解しやすさ**: 既存のTrainingタブと同じ実装パターンなので、他の開発者も理解しやすい
4. **メンテナンス性**: 手動マッピングの更新が不要
5. **処理フローの明確化**: Trainingタブの処理フローを分解し、Minimalタブは「パラメータ生成部分」のみを置き換える

### 関連ドキュメント

- **実装アプローチの詳細**: [AlternativeApproach.md](AlternativeApproach.md)
- **Trainingタブの挙動調査**: [investigation/lora_start_training_flow.md](investigation/lora_start_training_flow.md)
- **settings_list の構築**: `kohya_gui/lora_gui.py` 2800行目以降

### 注意事項

- Minimalタブでは、UIコンポーネントを全て構築する必要はない（パラメータ値のみを扱う）
- Trainingパラメータの生成は、既存のTrainingタブの実装パターンを再利用
- `settings_list` の構築は、既存の `lora_gui.py` のロジックを関数化して再利用
- `settings_list` の順序は、Trainingタブの `settings_list` 構築ロジック（2800行目以降）と同じ順序を維持する必要がある
