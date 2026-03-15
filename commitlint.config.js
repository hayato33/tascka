// commitlint設定。
// Conventional Commits（feat:, fix:, chore: 等）のフォーマットを強制する。
// Huskyのcommit-msgフックから呼び出される。
module.exports = {
  extends: ["@commitlint/config-conventional"],
};
