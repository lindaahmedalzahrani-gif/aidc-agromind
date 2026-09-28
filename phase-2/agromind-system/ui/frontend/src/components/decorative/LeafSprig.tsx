interface LeafSprigProps {
  className?: string;
}

/**
 * A quiet, original line-art botanical sprig used once in the hero as the
 * page's single decorative flourish. Deliberately spare: a stem with a few
 * asymmetric leaves, drawn only in outline so it reads as a sketch rather
 * than an illustration competing with the diagnosis panel.
 */
export function LeafSprig({ className }: LeafSprigProps) {
  return (
    <svg
      className={className}
      viewBox="0 0 220 320"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      <path
        d="M110 300C104 230 100 150 118 40"
        stroke="var(--color-sage)"
        strokeWidth="1.4"
        strokeLinecap="round"
      />
      <path
        d="M118 250C95 240 78 218 74 186C104 192 122 210 126 240Z"
        stroke="var(--color-sage)"
        strokeWidth="1.4"
        strokeLinejoin="round"
      />
      <path
        d="M120 195C144 183 158 160 160 128C132 138 116 158 114 190Z"
        stroke="var(--color-sage)"
        strokeWidth="1.4"
        strokeLinejoin="round"
      />
      <path
        d="M116 140C95 128 82 106 80 76C108 84 124 102 128 132Z"
        stroke="var(--color-sage)"
        strokeWidth="1.4"
        strokeLinejoin="round"
      />
      <path
        d="M119 90C138 78 148 58 148 32C124 42 112 60 111 86Z"
        stroke="var(--color-moss)"
        strokeWidth="1.4"
        strokeLinejoin="round"
      />
      <circle cx="118" cy="34" r="3.2" fill="var(--color-clay)" />
    </svg>
  );
}
