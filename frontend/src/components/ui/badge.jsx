import * as React from "react";
import { cva } from "class-variance-authority";
import { cn } from "@/utils/cn";

const badgeVariants = cva(
  "inline-flex items-center gap-1.5 rounded-full px-4 py-1.5 text-sm font-bold transition-all duration-200",
  {
    variants: {
      variant: {
        default: "bg-primary-100 text-primary-700",
        primary: "bg-primary-500 text-white shadow-md",
        secondary: "bg-primary-200 text-primary-800",
        success: "bg-green-100 text-green-700 border-2 border-green-200",
        warning: "bg-amber-100 text-amber-700 border-2 border-amber-200",
        error: "bg-red-100 text-red-600 border-2 border-red-200",
        outline: "border-2 border-primary-300 text-primary-600 bg-white",
        // Fun variants for kids
        fun: "bg-gradient-to-r from-accent-yellow to-accent-orange text-white shadow-md",
        star: "bg-gradient-to-r from-accent-pink to-accent-purple text-white shadow-md",
        // Status variants
        online: "bg-green-100 text-green-700 border-2 border-green-300",
        offline: "bg-amber-100 text-amber-700 border-2 border-amber-300",
        connecting: "bg-primary-100 text-primary-600",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

function Badge({ className, variant, ...props }) {
  return (
    <span className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}

export { Badge, badgeVariants };
