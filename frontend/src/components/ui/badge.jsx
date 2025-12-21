import * as React from "react";
import { cva } from "class-variance-authority";
import { cn } from "@/utils/cn";

const badgeVariants = cva(
  "inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium transition-colors",
  {
    variants: {
      variant: {
        default: "bg-slate-100 text-slate-700",
        primary: "bg-indigo-100 text-indigo-700",
        secondary: "bg-purple-100 text-purple-700",
        success: "bg-green-100 text-green-700",
        warning: "bg-amber-100 text-amber-700",
        error: "bg-red-100 text-red-700",
        outline: "border border-slate-200 text-slate-600",
        // Status variants
        online: "bg-green-100 text-green-700",
        offline: "bg-amber-100 text-amber-700",
        connecting: "bg-slate-100 text-slate-500",
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
