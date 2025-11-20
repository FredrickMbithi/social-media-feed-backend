# Core Queries

type Query {
posts(page: Int, perPage: Int): PostConnection!
post(id: ID!): Post
userPosts(userId: ID!): [Post!]!
}

# Core Mutations

type Mutation {
createPost(content: String!, imageUrl: String): Post!
createComment(postId: ID!, content: String!): Comment!
likePost(postId: ID!): Post!
sharePost(postId: ID!): Post!
deletePost(id: ID!): Boolean!
}

# Types

type Post {
id: ID!
author: User!
content: String!
imageUrl: String
likesCount: Int!
commentsCount: Int!
sharesCount: Int!
comments: [Comment!]!
createdAt: DateTime!
}
