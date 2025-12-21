import * as React from "react";
import { cva } from "class-variance-authority";
import { cn } from "@/utils/cn";

const badgeVariants = cva(
  "inline-flex items-center gap-1 rounded px-2 py-0.5 text-xs font-medium",
  {
    variants: {
      variant: {
        default: "bg-neutral-100 text-neutral-600",
        success: "bg-grammarly-green-light text-grammarly-green-dark",
        warning: "bg-grammarly-orange-light text-grammarly-orange",
        error: "bg-grammarly-red-light text-grammarly-red",
        info: "bg-grammarly-blue-light text-grammarly-blue",
        outline: "border border-neutral-300 text-neutral-600",
        online: "bg-grammarly-green-light text-grammarly-green-dark",
        offline: "bg-grammarly-orange-light text-grammarly-orange",
        connecting: "bg-neutral-100 text-neutral-500",
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
