import React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Link } from "react-router-dom";
import {
  Eye,
  EyeOff,
  User,
  Lock,
  Mail,
  FileText,
  Award,
  Stethoscope,
} from "lucide-react";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../ui/card";
import { Alert, AlertDescription } from "../ui/alert";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../ui/select";
import { useAuth } from "../../contexts/AuthContext";

const registerDoctorSchema = z
  .object({
    username: z.string().min(3, "Username must be at least 3 characters"),
    password: z.string().min(6, "Password must be at least 6 characters"),
    confirm_password: z.string().min(6, "Please confirm your password"),
    full_name: z.string().min(2, "Full name must be at least 2 characters"),
    specialty: z.string().min(2, "Specialty is required"),
    license_number: z.string().min(3, "License number is required"),
    contact: z.string().email("Please enter a valid email address"),
  })
  .refine((data) => data.password === data.confirm_password, {
    message: "Passwords don't match",
    path: ["confirm_password"],
  });

type RegisterDoctorFormData = z.infer<typeof registerDoctorSchema>;

interface RegisterDoctorFormProps {
  onSuccess?: () => void;
}

// Common medical specialties
const MEDICAL_SPECIALTIES = [
  "Cardiology",
  "Dermatology",
  "Emergency Medicine",
  "Family Medicine",
  "Gastroenterology",
  "General Surgery",
  "Internal Medicine",
  "Neurology",
  "Obstetrics and Gynecology",
  "Oncology",
  "Ophthalmology",
  "Orthopedics",
  "Pediatrics",
  "Psychiatry",
  "Radiology",
  "Urology",
  "Other",
];

export const RegisterDoctorForm: React.FC<RegisterDoctorFormProps> = ({
  onSuccess,
}) => {
  const [showPassword, setShowPassword] = React.useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = React.useState(false);
  const { registerDoctor, isLoading, error } = useAuth();

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm<RegisterDoctorFormData>({
    resolver: zodResolver(registerDoctorSchema),
  });

  const onSubmit = async (data: RegisterDoctorFormData) => {
    try {
      await registerDoctor(data);
      onSuccess?.();
    } catch (error) {
      // Error is handled by the AuthContext
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-cyan-50 p-4">
      <Card className="w-full max-w-2xl shadow-xl border-0 bg-white/80 backdrop-blur-sm">
        <CardHeader className="space-y-4 text-center">
          <div className="mx-auto w-16 h-16 bg-gradient-to-r from-green-500 to-blue-500 rounded-full flex items-center justify-center">
            <Stethoscope className="w-8 h-8 text-white" />
          </div>
          <div>
            <CardTitle className="text-2xl font-bold bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent">
              Doctor Registration
            </CardTitle>
            <CardDescription className="text-gray-600 mt-2">
              Join our healthcare platform as a medical professional
            </CardDescription>
          </div>
        </CardHeader>

        <CardContent className="space-y-6">
          {error && (
            <Alert className="border-red-200 bg-red-50">
              <AlertDescription className="text-red-700">
                {error}
              </AlertDescription>
            </Alert>
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {/* Username and Full Name */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label
                  htmlFor="username"
                  className="text-sm font-medium text-gray-700"
                >
                  Username *
                </Label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <Input
                    id="username"
                    type="text"
                    placeholder="Choose a username"
                    className="pl-10 h-11 border-gray-200 focus:border-green-500 focus:ring-green-500"
                    {...register("username")}
                  />
                </div>
                {errors.username && (
                  <p className="text-sm text-red-600">
                    {errors.username.message}
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <Label
                  htmlFor="full_name"
                  className="text-sm font-medium text-gray-700"
                >
                  Full Name *
                </Label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <Input
                    id="full_name"
                    type="text"
                    placeholder="Enter your full name"
                    className="pl-10 h-11 border-gray-200 focus:border-green-500 focus:ring-green-500"
                    {...register("full_name")}
                  />
                </div>
                {errors.full_name && (
                  <p className="text-sm text-red-600">
                    {errors.full_name.message}
                  </p>
                )}
              </div>
            </div>

            {/* Password Fields */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label
                  htmlFor="password"
                  className="text-sm font-medium text-gray-700"
                >
                  Password *
                </Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    placeholder="Create a password"
                    className="pl-10 pr-10 h-11 border-gray-200 focus:border-green-500 focus:ring-green-500"
                    {...register("password")}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showPassword ? (
                      <EyeOff className="w-4 h-4" />
                    ) : (
                      <Eye className="w-4 h-4" />
                    )}
                  </button>
                </div>
                {errors.password && (
                  <p className="text-sm text-red-600">
                    {errors.password.message}
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <Label
                  htmlFor="confirm_password"
                  className="text-sm font-medium text-gray-700"
                >
                  Confirm Password *
                </Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <Input
                    id="confirm_password"
                    type={showConfirmPassword ? "text" : "password"}
                    placeholder="Confirm your password"
                    className="pl-10 pr-10 h-11 border-gray-200 focus:border-green-500 focus:ring-green-500"
                    {...register("confirm_password")}
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showConfirmPassword ? (
                      <EyeOff className="w-4 h-4" />
                    ) : (
                      <Eye className="w-4 h-4" />
                    )}
                  </button>
                </div>
                {errors.confirm_password && (
                  <p className="text-sm text-red-600">
                    {errors.confirm_password.message}
                  </p>
                )}
              </div>
            </div>

            {/* Email and Specialty */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label
                  htmlFor="contact"
                  className="text-sm font-medium text-gray-700"
                >
                  Email Address *
                </Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <Input
                    id="contact"
                    type="email"
                    placeholder="Enter your email"
                    className="pl-10 h-11 border-gray-200 focus:border-green-500 focus:ring-green-500"
                    {...register("contact")}
                  />
                </div>
                {errors.contact && (
                  <p className="text-sm text-red-600">
                    {errors.contact.message}
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <Label
                  htmlFor="specialty"
                  className="text-sm font-medium text-gray-700"
                >
                  Medical Specialty *
                </Label>
                <Select onValueChange={(value) => setValue("specialty", value)}>
                  <SelectTrigger className="h-11 border-gray-200 focus:border-green-500 focus:ring-green-500">
                    <SelectValue placeholder="Select your specialty" />
                  </SelectTrigger>
                  <SelectContent>
                    {MEDICAL_SPECIALTIES.map((specialty) => (
                      <SelectItem key={specialty} value={specialty}>
                        {specialty}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.specialty && (
                  <p className="text-sm text-red-600">
                    {errors.specialty.message}
                  </p>
                )}
              </div>
            </div>

            {/* License Number */}
            <div className="space-y-2">
              <Label
                htmlFor="license_number"
                className="text-sm font-medium text-gray-700"
              >
                Medical License Number *
              </Label>
              <div className="relative">
                <Award className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <Input
                  id="license_number"
                  type="text"
                  placeholder="Enter your medical license number"
                  className="pl-10 h-11 border-gray-200 focus:border-green-500 focus:ring-green-500"
                  {...register("license_number")}
                />
              </div>
              {errors.license_number && (
                <p className="text-sm text-red-600">
                  {errors.license_number.message}
                </p>
              )}
            </div>

            <Button
              type="submit"
              className="w-full h-11 bg-gradient-to-r from-green-500 to-blue-500 hover:from-green-600 hover:to-blue-600 text-white font-medium transition-all duration-200 transform hover:scale-[1.02]"
              disabled={isLoading}
            >
              {isLoading ? "Creating Account..." : "Register as Doctor"}
            </Button>
          </form>

          <div className="text-center">
            <p className="text-sm text-gray-600">
              Already have an account?{" "}
              <Link
                to="/login"
                className="font-medium text-green-600 hover:text-green-500 transition-colors"
              >
                Sign in here
              </Link>
            </p>
            <p className="text-sm text-gray-600 mt-2">
              Want to register as a patient?{" "}
              <Link
                to="/register"
                className="font-medium text-blue-600 hover:text-blue-500 transition-colors"
              >
                Patient Registration
              </Link>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
