import { motion, type HTMLMotionProps } from 'framer-motion'
import type { ReactNode } from 'react'

type Props = {
  children: ReactNode
  className?: string
  delay?: number
  /** 0–1 how much of element must be visible */
  amount?: number | 'some' | 'all'
} & Omit<HTMLMotionProps<'div'>, 'children'>

export function ScrollReveal({
  children,
  className = '',
  delay = 0,
  amount = 0.25,
  ...rest
}: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 36 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-72px 0px -48px 0px', amount }}
      transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1], delay }}
      className={className}
      {...rest}
    >
      {children}
    </motion.div>
  )
}
