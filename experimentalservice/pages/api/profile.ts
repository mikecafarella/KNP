import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

export default async function handle(req, res) {
  const profile = await prisma.profile.create({
    data: {
      bio: "Hello World",
      user: {
        connect: { email: "alice@prisma.io" },
      },
    },
  });
}
