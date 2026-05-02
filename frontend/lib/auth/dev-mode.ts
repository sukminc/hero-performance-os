export function isDevLoginEnabled() {
  return process.env.OPB_ENABLE_DEV_LOGIN === "1" || process.env.NODE_ENV !== "production";
}
