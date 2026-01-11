了解です。
では **「同僚に説明でき、そのまま実装に着手できるレベル」**の **実装仕様書（サンプル）** を提案します。
これは **README / Confluence / 社内Wiki にそのまま貼れる文書**として書きます。

---

# SDXL専用 LoRA簡易タブ

## 実装仕様書（提案）

---

## 1. 目的

本仕様は、`kohya_ss` に **SDXL顔LoRA作成に特化した簡易タブ**を追加するための実装指針を定める。

本タブの目的は以下である。

* SDXL顔LoRA作成時に **毎回触る必要のある最小限のパラメータのみをUI化**する
* repeat や caption など、**GUI外ルール依存による事故を防止**する
* kohya-ss 本体の学習ロジックを変更せず、**GUI拡張として完結**させる
* 将来的に **容易に削除・無効化できる設計**とする

---

## 2. 設計方針（重要）

### 2.1 変更範囲の制約

* `train_network.py` 等の学習コアには **一切手を入れない**
* upstream の改造は **GUI起点に限定**
* 独自実装は `custom/` ディレクトリ配下に閉じる

### 2.2 本タブの位置づけ

* 新しい学習方式を追加するものではない
* **既存の kohya-ss 学習方式を安全に使うための補助UI**

### 2.3 「Start Training」ボタンの挙動（設計思想）

**Minimalタブの「Start Training」ボタンは、LoRAタブのTrainingタブの「Start Training」ボタンの挙動を模倣する。**

この設計思想により、以下の利点が得られます：

1. **一貫性**: Trainingタブと同じ実装パターンを使用することで、コードの一貫性が保たれる
2. **保守性**: `train_model` 関数のシグネチャが変更されても、自動的に対応される
3. **理解しやすさ**: 既存のTrainingタブと同じ実装パターンなので、他の開発者も理解しやすい
4. **メンテナンス性**: 手動マッピングの更新が不要
5. **処理フローの明確化**: Trainingタブの処理フローを分解し、Minimalタブは「パラメータ生成部分」のみを置き換える

詳細な処理フローは「8. 学習実行時の処理フロー」を参照してください。

---

## 3. ディレクトリ構成（提案）

```text
kohya_ss/
├─ kohya_gui.py                # upstream（最小フックのみ追加）
├─ kohya_gui/                  # upstream GUI群
└─ custom/
   ├─ __init__.py
   ├─ sdxl_simple_tab.py       # 本タブUI本体
   ├─ caption_tools.py         # caption一括生成ロジック
   ├─ dataset_config.py        # dataset_config生成
   ├─ state.py                 # custom状態管理
   └─ README.md                # このタブ専用説明
```

※ `custom/` を削除すれば機能ごと消える構成。

---

## 4. kohya_gui.py 側の最小変更

### 目的

* custom タブを **存在する場合のみ読み込む**
* custom が壊れていても upstream GUI が落ちない

### 実装方針（サンプル）

```python
def try_register_custom_tabs(gr):
    try:
        from custom.sdxl_simple_tab import register_tab
        register_tab(gr)
    except Exception as e:
        print(f"[custom tab disabled] {e}")
```

既存タブ定義の最後で呼び出す。

---

## 5. タブUI仕様

### 5.1 対象スコープ

* SDXL 専用
* 顔LoRA前提
* 単一 dataset / subset

---

### 5.2 UI項目一覧（確定）

#### モデル

* Checkpoint（Dropdown + Textbox）

  * 例：

    ```
    E:/Models/SDXL/harukiMIX_illustrious_v40.safetensors
    ```

#### 学習データ

* Image folder（親フォルダ指定）

  ```
  E:/LoRA/training_data/SATOMI
  ```

#### Repeat

* num_repeats（Integer）

  * 例：`5`

#### 学習量

* Epoch（Integer）

  * 例：`6`
* Max train steps（Integer）

  * 例：`1600`

#### 学習率

* U-Net LR

  * 例：`1e-4`
* Text Encoder LR

  * 例：`5e-5`

#### LoRA Network

* Rank (dim)

  * 例：`16`
* Alpha

  * 例：`16`

#### 解像度

* Resolution（固定 or Dropdown）

  * `512 x 512`

#### Batch

* Train batch size

  * `1`

#### Cache

* Cache latents（ON/OFF）
* Cache latents to disk（ON/OFF）

#### Caption

* 共通 Caption（Textbox）

  ```
  satomi_lora, 1girl
  ```
* 「caption一括生成」ボタン

#### 出力

* Output name

  * `SATOMI_001`
* Output folder

  ```
  E:/LoRA/outputs
  ```

---

## 6. Caption一括生成機能（実装仕様）

### 6.1 挙動

* Image folder 内の画像（`.jpg/.png`）を走査
* 同名の `.txt` を生成
* 既存 `.txt` がある場合は **必ず確認ダイアログ**

### 6.2 上書き確認

* 選択肢

  * 上書きする
  * スキップ
  * キャンセル

### 6.3 ログ出力

```
対象画像: 90
新規作成: 90
上書き: 0
スキップ: 0
```

---

## 7. Repeat（num_repeats）実装方式

### 方針

* フォルダ名 repeat 方式は使用しない
* `dataset_config.toml` を **動的生成**

### 生成例

```toml
[[datasets]]
resolution = [512, 512]

  [[datasets.subsets]]
  image_dir = "E:/LoRA/training_data/SATOMI"
  num_repeats = 5
```

### 学習時

* `--dataset_config <temp_path>` を付与
* `train_data_dir` 依存を回避

---

## 8. 学習実行時の処理フロー

### 8.1 設計思想

**Minimalタブの「Start Training」ボタンは、LoRAタブのTrainingタブの「Start Training」ボタンの挙動を模倣する。**

これは、Minimalタブの設計思想を実現するための重要な要件です。既存のTrainingタブと同じ実装パターンを使用することで、コードの一貫性と保守性を確保します。

### 8.2 処理フローの詳細

Minimalタブの「Start Training」ボタン押下時の処理フロー：

1. **Minimalタブの「Start Training」押下**
   - MinimalタブのUIから16個のパラメータを取得
   - UI入力値を検証

2. **Minimalパラメータ生成**
   - MinimalタブのUI入力値から、16個のパラメータを辞書形式で生成
   - 例: `pretrained_model_name_or_path`, `train_data_dir`, `output_name`, `output_dir`, `learning_rate`, `text_encoder_lr`, `network_dim`, `network_alpha`, `epoch`, `max_train_steps`, `max_resolution`, `train_batch_size`, `cache_latents`, `cache_latents_to_disk`, `save_model_as`, `save_precision`

3. **Trainingパラメータ生成**
   - 既存のTrainingタブと同じように、全243個のパラメータをデフォルト値で生成
   - Trainingタブの `settings_list` 構築ロジック（`kohya_gui/lora_gui.py` 2800行目以降）と同じ方法で、デフォルト値を生成
   - SDXL顔LoRA用の最適化済みデフォルト値を使用

4. **Minimalパラメータマージ**
   - Trainingパラメータ（243個、辞書形式）に、Minimalパラメータ（16個、辞書形式）を上書き
   - `final_params = {**training_params, **minimal_params}` の形式
   - Minimalタブで設定した値が優先される
   - マージ後のパラメータセット（243個）が完成

5. **settings_list の構築**
   - マージ後のパラメータセットから、Trainingタブと同じ順序で `settings_list` を構築
   - `kohya_gui/lora_gui.py` 2800行目以降の `settings_list` 構築ロジックを関数化して再利用
   - `settings_list` の順序は、Trainingタブの `settings_list` 構築ロジックと同じ順序を維持

6. **トレーニング開始**
   - 既存の `train_model` 関数を、Trainingタブと同じ方法で呼び出す
   - `train_model(headless, print_only, *settings_list)` の形式
   - 以降の処理（バリデーション、コマンド構築、プロセス起動）は、Trainingタブと同じフロー

### 8.3 Trainingタブとの比較

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

### 8.4 実装上の注意事項

- **UIコンポーネントの構築**: Minimalタブでは、UIコンポーネントを全て構築する必要はない（パラメータ値のみを扱う）
- **デフォルト値の生成**: Trainingパラメータの生成は、既存のTrainingタブの実装パターンを再利用
- **settings_list の構築**: `settings_list` の構築は、既存の `lora_gui.py` のロジックを関数化して再利用
- **順序の維持**: `settings_list` の順序は、Trainingタブの `settings_list` 構築ロジック（2800行目以降）と同じ順序を維持する必要がある

### 8.5 関連ドキュメント

- **設計要件の詳細**: [Design_Requirement_001.md](Design_Requirement_001.md)
- **実装アプローチの詳細**: [AlternativeApproach.md](AlternativeApproach.md)
- **Trainingタブの挙動調査**: [investigation/lora_start_training_flow.md](investigation/lora_start_training_flow.md)

---

## 9. 意図的に実装しない項目

以下は **設計判断としてUIに出さない**。

* optimizer / lr scheduler
* network_module / network_args
* 正則化画像
* 複数 dataset
* フォルダ名 repeat 方式

理由：

* 操作ミスが増える
* 本タブの目的（再現性・安定性）から外れる

---

## 10. 切り捨て・無効化ポリシー

* `custom/` ディレクトリ削除で完全無効化
* kohya-ss 本体に影響なし
* upstream 更新時の衝突は最小

---

## 11. 一文まとめ（実装者向け）

> このタブは
> **SDXL顔LoRAを、事故なく・毎回同じ考え方で作るための
> 最小操作UIを追加するだけの拡張**である。
>
> 学習の中身は変えない。
> 変えるのは「迷い」と「ミス」だけ。
