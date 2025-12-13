import Link from "next/link"
import { Card } from "@/components/ui/card"

const items = [
  { label: "従業員情報編集", href: "/admin/edit_db/employees" },
  { label: "設問編集", href: "/admin/edit_db/questions" },
  { label: "評価シート編集", href: "/admin/edit_db/forms" },
  { label: "アカウント編集", href: "/admin/edit_db/accounts" },
]

export default function EditDbPage() {
  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold">データ編集</h1>
      <div className="grid grid-cols-2 gap-4">
        {items.map((i) => (
          <Link key={i.href} href={i.href}>
            <Card className="p-4 hover:bg-muted transition">
              {i.label}
            </Card>
          </Link>
        ))}
      </div>
    </div>
  )
}
