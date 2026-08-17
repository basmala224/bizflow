import { Route, Routes } from 'react-router-dom'

function Home() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50">
      <div className="text-center">
        <h1 className="text-3xl font-semibold text-gray-900">BizFlow</h1>
        <p className="mt-2 text-gray-500">Frontend scaffold ready.</p>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
    </Routes>
  )
}
