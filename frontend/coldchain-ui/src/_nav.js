import React from 'react'
import CIcon from '@coreui/icons-react'
import { CNavItem } from '@coreui/react'
import { cilSpeedometer, cilStorage, cilTruck, cilChartLine, cilLoop } from '@coreui/icons'

const _nav = [
  {
    component: 'CNavItem',
    name: 'Dashboard',
    to: '/dashboard',
    icon: <CIcon icon={cilSpeedometer} customClassName="nav-icon" />,
  },
  {
    component: 'CNavItem',
    name: 'Storage Monitoring',
    to: '/storage',
    icon: <CIcon icon={cilStorage} customClassName="nav-icon" />,
  },
  {
    component: 'CNavItem',
    name: 'Transport',
    to: '/transport',
    icon: <CIcon icon={cilTruck} customClassName="nav-icon" />,
  },
  {
    component: 'CNavItem',
    name: 'Analytics',
    to: '/analytics',
    icon: <CIcon icon={cilChartLine} customClassName="nav-icon" />,
  },
  {
    component: 'CNavItem',
    name: 'Model Feedback',
    to: '/feedback',
    icon: <CIcon icon={cilLoop} customClassName="nav-icon" />,
  },
]

export default _nav
