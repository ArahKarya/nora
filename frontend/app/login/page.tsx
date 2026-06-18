"use client";

import { useRouter } from "next/navigation";
import AuthCard from "@/components/AuthCard";
import { login } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  return (
    <AuthCard
      mode="login"
      altHref="/register"
      altLabel="Belum punya akun? Daftar"
      onSubmit={async (email, password) => {
        await login(email, password);
        router.push("/");
      }}
    />
  );
}
