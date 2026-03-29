import { useRef, useState, type ReactNode } from 'react'
import { motion, type HTMLMotionProps } from 'framer-motion'

type Props = Omit<HTMLMotionProps<'button'>, 'children'> & { children: ReactNode }

export function RippleButton({ children, className = '', onClick, ...rest }: Props) {
  const btnRef = useRef<HTMLButtonElement>(null)
  const [ripples, setRipples] = useState<{ id: number; x: number; y: number }[]>([])
  const nextId = useRef(0)

  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    const el = btnRef.current
    if (el) {
      const rect = el.getBoundingClientRect()
      const id = ++nextId.current
      setRipples((r) => [...r, { id, x: e.clientX - rect.left, y: e.clientY - rect.top }])
      window.setTimeout(() => {
        setRipples((r) => r.filter((x) => x.id !== id))
      }, 650)
    }
    onClick?.(e)
  }

  const { disabled, ...btnProps } = rest

  return (
    <motion.button
      ref={btnRef}
      type="button"
      className={`relative overflow-hidden ${className}`}
      onClick={handleClick}
      disabled={disabled}
      whileHover={disabled ? {} : { scale: 1.02 }}
      whileTap={disabled ? {} : { scale: 0.98 }}
      transition={{ type: 'spring', stiffness: 480, damping: 28 }}
      {...btnProps}
    >
      {ripples.map((r) => (
        <motion.span
          key={r.id}
          className="pointer-events-none absolute z-[5] h-8 w-8 -translate-x-1/2 -translate-y-1/2 rounded-full bg-white/35"
          style={{ left: r.x, top: r.y }}
          initial={{ scale: 0, opacity: 0.55 }}
          animate={{ scale: 14, opacity: 0 }}
          transition={{ duration: 0.65, ease: [0.22, 1, 0.36, 1] }}
        />
      ))}
      {children}
    </motion.button>
  )
}
