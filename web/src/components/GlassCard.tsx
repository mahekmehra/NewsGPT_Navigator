import { motion, type HTMLMotionProps } from 'framer-motion'
import type { ReactNode } from 'react'

type Props = {
  children: ReactNode
  className?: string
  delay?: number
} & Omit<HTMLMotionProps<'div'>, 'children'>

export function GlassCard({ children, className = '', delay = 0, ...rest }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{
        y: -3,
        scale: 1.018,
        boxShadow:
          '0 0 0 1px rgba(129, 140, 248, 0.2), 0 20px 40px -14px rgba(0,0,0,0.5), 0 0 40px -10px rgba(99, 102, 241, 0.22)',
      }}
      transition={{ type: 'spring', stiffness: 420, damping: 28, delay }}
      className={`glass-panel rounded-2xl p-5 ${className}`}
      {...rest}
    >
      {children}
    </motion.div>
  )
}
