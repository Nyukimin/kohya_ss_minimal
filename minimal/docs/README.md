# Minimal プロジェクト ドキュメント

このディレクトリには、Minimalタブプロジェクトに関するドキュメントを格納しています。

## ファイル構成

### 仕様書

- **Specification_001.md** - プロジェクトの基本仕様と要求事項

### 実装仕様書

- **ImplementationSpecification_FULL.md** - 実装仕様書（完全版・最新設計思想反映）
- **ImplementationSpecification_001.md** - 実装仕様書 v1.0
- **ImplementationSpecification_002.md** - 実装仕様書 v2.0
- **ImplementationSpecification_002_revised.md** - 実装仕様書 v2.0（修正版）
- **ImplementationSpecification_003.md** - 実装仕様書 v3.0
- **ImplementationSpecification_004.md** - 実装仕様書 v4.0（現状実装反映）

### 実装提案

- **AlternativeApproach.md** - Minimalタブの代替アプローチ提案（「Kohya-ssのパラメータ生成 → Minimalの設定で上書き → プロセス起動」）

### 設計要件

- **Design_Requirement_001.md** - Minimalタブの「Start Training」ボタンの挙動要件（Trainingタブの挙動を模倣）

### 検証レポート

- **PARAMETER_VERIFICATION_REPORT.md** - パラメータ形式検証レポート

### 調査資料

- **investigation/** - kohya-ss本体の挙動調査資料
  - `process_startup_flow.md` - kohya-ss起動プロセスフロー
  - `lora_start_training_flow.md` - LoRAタブの挙動調査

## ドキュメントの読み方

1. **プロジェクトの概要を理解する**: `Specification_001.md` から読み始める
2. **実装仕様を確認する**: `ImplementationSpecification_FULL.md` が最新の設計思想を反映した完全版
3. **実装の現状を確認する**: `ImplementationSpecification_004.md` が最新の実装状況を反映
4. **実装方針を検討する**: `AlternativeApproach.md` で代替アプローチを検討
5. **設計要件を確認する**: `Design_Requirement_001.md` で「Start Training」ボタンの挙動要件を確認

## 関連ドキュメント

- **調査資料**: `investigation/` ディレクトリに、kohya-ss本体の挙動調査資料を格納
