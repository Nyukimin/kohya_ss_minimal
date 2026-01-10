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

1. UI入力を custom_state に保存
2. 「学習開始」押下
3. dataset_config.toml を生成
4. pretrained_model を UI値で上書き
5. 既存 kohya-ss の学習実行処理を呼び出す

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
