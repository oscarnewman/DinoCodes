import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { VerifyController } from './verify/verify.controller';

@Module({
  imports: [],
  controllers: [AppController, VerifyController],
  providers: [AppService],
})
export class AppModule {}
