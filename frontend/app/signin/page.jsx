"use client"

import { useState } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Eye, EyeOff } from "lucide-react"
import axios from 'axios'
import { cn } from "@/lib/utils";
import { buttonVariants } from "@/components/ui/button";

export default function SignInPage() {
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const router = useRouter()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      const response = await axios.post(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/login`, { email, password }, {
        withCredentials: true // 🔥 This is the magic!
      })
      console.log('Login successful:', response.data)
      router.push("/dashboard")
    } catch (error) {
      console.error('Login failed:', error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center p-4 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-blue-900 via-black to-black text-white">
      <Card className="w-full max-w-md border-primary-400 shadow-lg">
        <CardHeader className="space-y-1  rounded-t-lg">
          <CardTitle className="text-2xl font-bold text-center text-white">Sign in to VariantWise</CardTitle>
          <CardDescription className="text-center text-primary-200">
            Enter your email and password to access your account
          </CardDescription>
        </CardHeader>
        <CardContent className="pt-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email" className="text-white">
                Email
              </Label>
              <Input
                id="email"
                type="email"
                placeholder="name@example.com"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="transition-all duration-200 focus:ring-2 focus:ring-primary-300 border-primary-300 bg-primary-500 text-white placeholder:text-primary-300"
              />
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="password" className="text-white">
                  Password
                </Label>
                <Link href="/forgot-password" className="text-sm text-primary-200 hover:underline hover:text-white">
                  Forgot password?
                </Link>
              </div>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  placeholder="••••••••"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="pr-10 transition-all duration-200 focus:ring-2 focus:ring-primary-300 border-primary-300 bg-primary-500 text-white placeholder:text-primary-300"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-primary-200 hover:text-white"
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>
            <Button
              type="submit"
              className="w-full bg-black hover:bg-primary-500 text-white border border-primary-300"
              disabled={isLoading}
            >
              {isLoading ? "Signing in..." : "Sign in"}
            </Button>
          </form>
        </CardContent>
        <CardFooter className="flex flex-col space-y-4 border-t border-primary-400">
          <div className="relative flex items-center">
            <div className="flex-grow border-t border-primary-300"></div>
            <span className="mx-4 flex-shrink text-primary-200 text-sm">or</span>
            <div className="flex-grow border-t border-primary-300"></div>
          </div>
          <a
        href={`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/auth/google`}
        className={cn(
          buttonVariants({ variant: "outline" }), // Use buttonVariants for styling
          "w-full border-primary-300 text-white hover:bg-primary-500" // Add specific styles
        )}
      >
        Continue with Google
      </a>
          <div className="text-center text-sm text-primary-200">
            Don&apos;t have an account?{" "}
            <Link href="/signup" className="text-primary-100 hover:underline hover:text-white">
              Sign up
            </Link>
          </div>
        </CardFooter>
      </Card>
    </div>
  )
}