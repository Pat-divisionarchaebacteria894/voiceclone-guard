// Type declarations for packages that ship without bundler-compatible type exports.
// These shims let tsc resolve the modules while the actual types are inferred
// from usage or provided by the packages' runtime exports.

declare module "lucide-react" {
  import * as React from "react";

  export interface LucideProps extends React.SVGAttributes<SVGElement> {
    color?: string;
    size?: string | number;
    strokeWidth?: string | number;
    absoluteStrokeWidth?: boolean;
    className?: string;
  }

  export type LucideIcon = React.ForwardRefExoticComponent<
    LucideProps & React.RefAttributes<SVGSVGElement>
  >;

  // Icons used in this project
  export const ShieldCheck: LucideIcon;
  export const Upload: LucideIcon;
  export const Mic: LucideIcon;
  export const MicOff: LucideIcon;
  export const X: LucideIcon;
  export const FileAudio: LucideIcon;
  export const Loader2: LucideIcon;
  export const CheckCircle: LucideIcon;
  export const XCircle: LucideIcon;
  export const AlertTriangle: LucideIcon;
  export const Cpu: LucideIcon;
  export const BarChart3: LucideIcon;
  export const Clock: LucideIcon;
  export const Volume2: LucideIcon;
  export const Info: LucideIcon;
  export const Trash2: LucideIcon;
  export const RefreshCw: LucideIcon;
  export const ChevronLeft: LucideIcon;
  export const ChevronRight: LucideIcon;
}
