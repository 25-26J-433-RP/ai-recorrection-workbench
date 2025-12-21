import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva } from "class-variance-authority";
import { cn } from "@/utils/cn";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-grammarly-green focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default:
          "bg-grammarly-green text-white hover:bg-grammarly-green-dark",
        destructive:
          "bg-grammarly-red text-white hover:bg-red-600",
        outline:
          "border border-neutral-300 bg-white text-neutral-700 hover:bg-neutral-50",
        secondary:
          "bg-neutral-100 text-neutral-700 hover:bg-neutral-200",
        ghost: "text-neutral-600 hover:bg-neutral-100",
        link: "text-grammarly-green underline-offset-4 hover:underline",
        success:
          "bg-grammarly-green text-white hover:bg-grammarly-green-dark",
      },
      size: {
        default: "h-9 px-4 py-2",
        sm: "h-8 rounded-md px-3 text-xs",
        lg: "h-10 px-6",
        icon: "h-9 w-9",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

const Button = React.forwardRef(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";

export { Button, buttonVariants };
