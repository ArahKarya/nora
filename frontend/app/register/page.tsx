"use client";

import { useRouter } from "next/navigation";
import AuthCard from "@/components/AuthCard";
import { register, login } from "@/lib/api";

export default function RegisterPage() {
  const router = useRouter();
  return (
    <AuthCard
      mode="register"
      altHref="/login"
      altLabel="Sudah punya akun? Masuk"
      onSubmit={async (email, password) => {
        await register(email, password);
        // auto-login setelah daftar
        await login(email, password);
        router.push("/");
      }}
    />
  );
}
