import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva } from "class-variance-authority";
import { cn } from "@/utils/cn";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-2xl text-base font-bold transition-all duration-300 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-5 [&_svg]:shrink-0 active:scale-95",
  {
    variants: {
      variant: {
        default:
          "bg-gradient-to-r from-primary-500 to-primary-600 text-white shadow-lg shadow-primary-500/30 hover:from-primary-600 hover:to-primary-700 hover:shadow-xl hover:shadow-primary-500/40 focus-visible:ring-primary-400",
        destructive:
          "bg-gradient-to-r from-red-400 to-red-500 text-white shadow-lg shadow-red-400/30 hover:from-red-500 hover:to-red-600 focus-visible:ring-red-300",
        outline:
          "border-2 border-primary-300 bg-white text-primary-700 shadow-sm hover:bg-primary-50 hover:border-primary-400 focus-visible:ring-primary-300",
        secondary:
          "bg-primary-100 text-primary-700 hover:bg-primary-200 focus-visible:ring-primary-300",
        ghost: "text-primary-600 hover:bg-primary-100 hover:text-primary-700",
        link: "text-primary-600 underline-offset-4 hover:underline",
        success:
          "bg-gradient-to-r from-green-400 to-green-500 text-white shadow-lg shadow-green-400/30 hover:from-green-500 hover:to-green-600 focus-visible:ring-green-300",
        fun:
          "bg-gradient-to-r from-accent-yellow via-accent-orange to-accent-pink text-white shadow-lg hover:shadow-xl focus-visible:ring-accent-yellow",
      },
      size: {
        default: "h-12 px-6 py-3",
        sm: "h-10 rounded-xl px-4 text-sm",
        lg: "h-14 rounded-2xl px-8 text-lg",
        icon: "h-12 w-12",
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
