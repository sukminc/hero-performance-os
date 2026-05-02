"use server";

import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { resolveRepoRoot, resolveSqlitePath } from "@/lib/uploads/runtime";

const execFileAsync = promisify(execFile);

export type DemoApplyState = {
  ok: boolean;
  message: string;
  applicationId?: string;
};

function fieldValue(formData: FormData, key: string) {
  const value = formData.get(key);
  return typeof value === "string" ? value : "";
}

export async function submitDemoApplication(
  _prevState: DemoApplyState | null,
  formData: FormData
): Promise<DemoApplyState> {
  const payload = {
    name: fieldValue(formData, "name"),
    email: fieldValue(formData, "email"),
    games: fieldValue(formData, "games"),
    help: fieldValue(formData, "help"),
  };

  try {
    const { stdout } = await execFileAsync(
      "python3",
      [
        "-c",
        [
          "import json",
          "from core.beta.demo_applications import submit_demo_application",
          `payload = ${JSON.stringify(payload)}`,
          "result = submit_demo_application(payload['name'], payload['email'], payload['games'], payload['help'])",
          "print(json.dumps(result, default=str))",
        ].join("; "),
      ],
      {
        cwd: resolveRepoRoot(),
        env: {
          ...process.env,
          PYTHONPATH: resolveRepoRoot(),
          SQLITE_DB_PATH: resolveSqlitePath(),
          V2_STORAGE_BACKEND: "sqlite",
        },
      }
    );
    const result = JSON.parse(stdout.trim());
    return {
      ok: Boolean(result.ok),
      message: String(result.message || "Application processed."),
      applicationId: result.application_id,
    };
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown application failure.";
    return { ok: false, message };
  }
}
