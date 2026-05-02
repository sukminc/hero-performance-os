import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { resolveRepoRoot, resolveSqlitePath } from "@/lib/uploads/runtime";

const execFileAsync = promisify(execFile);

export type DemoApplication = {
  id: string;
  name: string;
  email: string;
  games: string;
  help_goal: string;
  status: string;
  created_at: string;
  application_metadata: Record<string, unknown>;
};

export async function getDemoApplications(): Promise<DemoApplication[]> {
  try {
    const { stdout } = await execFileAsync(
      "python3",
      [
        "-c",
        [
          "import json",
          "from core.beta.demo_applications import list_demo_applications",
          "payload = list_demo_applications(limit=25)",
          "print(json.dumps(payload, default=str))",
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
    const payload = JSON.parse(stdout.trim());
    return payload.applications || [];
  } catch {
    return [];
  }
}
