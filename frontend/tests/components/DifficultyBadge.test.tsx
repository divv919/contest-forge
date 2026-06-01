import React from 'react'
import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { DifficultyBadge } from '@/components/problems/DifficultyBadge'

describe('DifficultyBadge', () => {
  it('renders label and badge structure', () => {
    render(<DifficultyBadge difficulty="MEDIUM" />)
    expect(screen.getByText('Medium')).toBeInTheDocument()
    const badge = screen.getByText('Medium')
    expect(badge.closest('[data-slot="badge"]')).toBeTruthy()
  })
})
