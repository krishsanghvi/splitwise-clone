import { Link, useLocation } from 'react-router-dom'

export function Sidebar() {
  const location = useLocation()

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: '📊' },
    { name: 'My Groups', href: '/groups', icon: '👥' },
    { name: 'All Expenses', href: '/expenses', icon: '💰' },
    { name: 'Balances', href: '/balances', icon: '⚖️' },
    { name: 'Settings', href: '/settings', icon: '⚙️' },
  ]

  return (
    <aside className="w-64 bg-gray-50 min-h-screen border-r border-gray-200">
      <div className="p-6">
        <nav className="space-y-2">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`
                  flex items-center space-x-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors
                  ${isActive 
                    ? 'bg-blue-100 text-blue-700 border border-blue-200' 
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                  }
                `}
              >
                <span className="text-lg">{item.icon}</span>
                <span>{item.name}</span>
              </Link>
            )
          })}
        </nav>
      </div>
    </aside>
  )
}