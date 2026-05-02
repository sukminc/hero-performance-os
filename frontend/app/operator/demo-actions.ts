"use server";

import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { revalidatePath } from "next/cache";
import { resolveRepoRoot, resolveSqlitePath } from "@/lib/uploads/runtime";

const execFileAsync = promisify(execFile);

async function runPython(code: string) {
  const { stdout } = await execFileAsync("python3", ["-c", code], {
    cwd: resolveRepoRoot(),
    env: {
      ...process.env,
      PYTHONPATH: resolveRepoRoot(),
      SQLITE_DB_PATH: resolveSqlitePath(),
      V2_STORAGE_BACKEND: "sqlite",
    },
  });
  return JSON.parse(stdout.trim());
}

export async function updateDemoApplicationStatus(formData: FormData) {
  const applicationId = String(formData.get("applicationId") || "");
  const status = String(formData.get("status") || "");
  await runPython(
    [
      "import json",
      "from core.beta.demo_applications import update_demo_application_status",
      `payload = update_demo_application_status(${JSON.stringify(applicationId)}, ${JSON.stringify(status)})`,
      "print(json.dumps(payload, default=str))",
    ].join("; ")
  );
  revalidatePath("/operator");
}

export async function provisionDemoApplication(formData: FormData) {
  const applicationId = String(formData.get("applicationId") || "");
  const playerId = String(formData.get("playerId") || "");
  await runPython(
    [
      "import json",
      "from core.beta.demo_applications import provision_demo_application_owner",
      `payload = provision_demo_application_owner(${JSON.stringify(applicationId)}, ${JSON.stringify(playerId)})`,
      "print(json.dumps(payload, default=str))",
    ].join("; ")
  );
  revalidatePath("/operator");
}

export async function tagBigWinSpot(formData: FormData) {
  const spotId = String(formData.get("spotId") || "");
  const decision = String(formData.get("decision") || "");
  const notes = String(formData.get("notes") || "");
  await runPython(
    [
      "import json",
      "from core.storage.repositories import V2Repository",
      "from core.surfaces.big_win_review import tag_big_win_spot",
      "repo = V2Repository()",
      "repo.ensure_schema()",
      `payload = tag_big_win_spot(repo, spot_id=${JSON.stringify(spotId)}, decision=${JSON.stringify(decision)}, notes=${JSON.stringify(notes)})`,
      "print(json.dumps(payload, default=str))",
    ].join("; ")
  );
  revalidatePath("/operator");
}
