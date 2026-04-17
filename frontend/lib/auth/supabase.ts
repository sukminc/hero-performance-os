import { cookies } from "next/headers";
import { createServerClient } from "@supabase/ssr";

export async function createSupabaseServerClient() {
  const cookieStore = await cookies();
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

  if (!supabaseUrl || !supabaseAnonKey) {
    return null;
  }

  return createServerClient(supabaseUrl, supabaseAnonKey, {
    cookies: {
      getAll() {
        return cookieStore.getAll();
      },
      setAll() {
        // App shell foundation only. Cookie writes will be added when auth actions are wired.
      }
    }
  });
}

export async function getCurrentUser() {
  const client = await createSupabaseServerClient();
  if (!client) {
    return null;
  }
  const { data } = await client.auth.getUser();
  return data.user ?? null;
}
