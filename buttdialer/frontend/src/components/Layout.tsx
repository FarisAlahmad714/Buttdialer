import { ReactNode } from 'react'
import Sidebar from './Sidebar'
import Header from './Header'
import Softphone from './Softphone'

interface LayoutProps {
  children: ReactNode
}

export default function Layout({ children }: LayoutProps) {
  return (
    <div className="h-screen flex bg-gray-50">
      <Sidebar />
      
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        
        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-50 p-6">
          {children}
        </main>
      </div>
      
      <Softphone />
    </div>
  )
}