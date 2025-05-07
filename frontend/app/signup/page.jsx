"use client"

import { useState } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { Eye, EyeOff } from "lucide-react"

export default function SignUpPage() {
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsLoading(true)

    // Simulate registration delay
    await new Promise((resolve) => setTimeout(resolve, 1500))

    // In a real app, you would register with a backend here
    setIsLoading(false)

    // Redirect to dashboard after successful registration
    router.push("/dashboard")
  }

  return (
    <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center p-4 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-blue-900 via-black to-black text-white">
      <Card className="w-full max-w-md border-primary-400 shadow-lg">
        <CardHeader className="space-y-1 rounded-t-lg">
          <CardTitle className="text-2xl font-bold text-center text-white">Create an account</CardTitle>
          <CardDescription className="text-center text-primary-200">
            Enter your information to create a VariantWise account
          </CardDescription>
        </CardHeader>
        <CardContent className="pt-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="firstName" className="text-white">
                  First name
                </Label>
                <Input
                  id="firstName"
                  placeholder="John"
                  required
                  className="transition-all duration-200 focus:ring-2 focus:ring-primary-300 border-primary-300 bg-primary-500 text-white placeholder:text-primary-300"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="lastName" className="text-white">
                  Last name
                </Label>
                <Input
                  id="lastName"
                  placeholder="Doe"
                  required
                  className="transition-all duration-200 focus:ring-2 focus:ring-primary-300 border-primary-300 bg-primary-500 text-white placeholder:text-primary-300"
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="email" className="text-white">
                Email
              </Label>
              <Input
                id="email"
                type="email"
                placeholder="name@example.com"
                required
                className="transition-all duration-200 focus:ring-2 focus:ring-primary-300 border-primary-300 bg-primary-500 text-white placeholder:text-primary-300"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password" className="text-white">
                Password
              </Label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  placeholder="••••••••"
                  required
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
              <p className="text-xs text-primary-200">Password must be at least 8 characters long</p>
            </div>
            <div className="flex items-center space-x-2">
              <Checkbox id="terms" required className="border-primary-300 text-black data-[state=checked]:bg-black" />
              <Label htmlFor="terms" className="text-sm text-primary-200">
                I agree to the{" "}
                <Link href="/terms" className="text-primary-100 hover:underline hover:text-white">
                  Terms of Service
                </Link>{" "}
                and{" "}
                <Link href="/privacy" className="text-primary-100 hover:underline hover:text-white">
                  Privacy Policy
                </Link>
              </Label>
            </div>
            <Button
              type="submit"
              className="w-full bg-black hover:bg-primary-500 text-white border border-primary-300"
              disabled={isLoading}
            >
              {isLoading ? "Creating account..." : "Create account"}
            </Button>
          </form>
        </CardContent>
        <CardFooter className="flex flex-col space-y-4 border-t border-primary-400">
          <div className="relative flex items-center">
            <div className="flex-grow border-t border-primary-300"></div>
            <span className="mx-4 flex-shrink text-primary-200 text-sm">or</span>
            <div className="flex-grow border-t border-primary-300"></div>
          </div>
          <Button variant="outline" className="w-full border-primary-300 text-white hover:bg-primary-500">
            Sign up with Google
          </Button>
          <div className="text-center text-sm text-primary-200">
            Already have an account?{" "}
            <Link href="/signin" className="text-primary-100 hover:underline hover:text-white">
              Sign in
            </Link>
          </div>
        </CardFooter>
      </Card>
    </div>
  )
}