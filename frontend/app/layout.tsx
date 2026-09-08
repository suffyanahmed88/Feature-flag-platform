import './globals.css'; import type { Metadata } from 'next'
export const metadata:Metadata={title:'Flagship | Feature Flags',description:'Feature flag control plane'}
export default function Layout({children}:{children:React.ReactNode}){return <html lang="en"><body>{children}</body></html>}
