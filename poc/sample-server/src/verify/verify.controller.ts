import {
  Body,
  Controller,
  NotFoundException,
  Post,
  UnauthorizedException,
} from '@nestjs/common';
import { IsNotEmpty, IsUUID } from 'class-validator';
import { totp } from 'otplib';

class VerifyTokenDTO {
  @IsNotEmpty()
  otp: string;

  @IsNotEmpty()
  @IsUUID()
  resourceId: number;
}

const resources = {
  '3372bb97-4086-4760-a6da-61c7eafe9c06': {
    id: '3372bb97-4086-4760-a6da-61c7eafe9c06',
    name: 'Sick Kanye Tickets',
    user: 'James Tompkin',
    date: new Date(),
    hasEntered: false,
  },
  'bdf037c2-cbea-449c-bb7c-e1026906b13c': {
    id: 'bdf037c2-cbea-449c-bb7c-e1026906b13c',
    name: 'Home Healthcare Check-in',
    provider: 'Isaac Hilton-VanOsdall',
    patient: 'Ben Gershuny',
    hasCheckedIn: true,
    tasks: ['Administer medicine', 'Check vitals'],
  },
};

@Controller('verify')
export class VerifyController {
  @Post()
  verify(@Body() token: VerifyTokenDTO): any {
    // Verify TOTP
    console.log(token);
    const { otp } = token;
    const isOtpValid = totp.check(
      otp,
      'HJWFMM2BOVAUSQTGNFBHCLDZKJ2G6TCDKIYV45CVOVUG4WDBKVRA',
    );

    if (!isOtpValid) {
      throw new UnauthorizedException(
        `One time token ${token.otp} has expired`,
      );
    }

    const resource = resources[token.resourceId];
    if (!resource) {
      throw new NotFoundException('Resource does not exist');
    }

    return resource;
  }
}
